"""Aria V3 -- AI Assistant with Memory.

Builds on V2 by adding AgentCore Memory with three extraction strategies:
- SessionSummarizer: summarizes conversations after they end
- PreferenceLearner: extracts user preferences (e.g., "I prefer Python")
- FactExtractor: extracts factual statements (e.g., "I work at Acme Corp")

Memory persists across sessions so Aria remembers users between conversations.

AgentCore Runtime provisions a dedicated microVM for each session, so
your agent code only ever handles one session at a time. The session_id
is passed to AgentCore Memory to namespace the conversation.

Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-memory.html
"""

import logging
import os

from bedrock_agentcore.runtime import BedrockAgentCoreApp

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
MEMORY_ID = os.environ.get("MEMORY_ID", "")

SYSTEM_PROMPT = """\
You are Aria, a personal AI assistant. You have the following capabilities:

1. **Code execution** -- You can run Python code for calculations, data analysis, \
charting, file generation, and general-purpose programming.

2. **Web browsing** -- You can browse the web to look up current information.

3. **Memory** -- You remember user preferences, facts, and conversation history across \
sessions. When you learn something about the user, it is automatically stored.

Guidelines:
- Be concise and helpful. Prefer structured output when it improves clarity.
- Proactively use your tools. Don't guess when you can look it up or calculate it.
- Reference what you remember about the user when relevant to the conversation.
- Never fabricate tool results or memories.
"""

app = BedrockAgentCoreApp()

# Created on first invocation, reused for the lifetime of the microVM.
# Runtime guarantees one session per microVM, so no multi-session management needed.
_agent = None


def _extract_actor_id(context) -> str:
    """Extract the user's actor ID from the JWT in the Authorization header."""
    try:
        headers = getattr(context, "request_headers", None) or {}
        auth_header = headers.get("Authorization", headers.get("authorization", ""))

        if auth_header.startswith("Bearer "):
            import base64
            import json as _json

            token = auth_header[7:]
            payload_b64 = token.split(".")[1]
            payload_b64 += "=" * (-len(payload_b64) % 4)
            claims = _json.loads(base64.urlsafe_b64decode(payload_b64))

            actor_id = claims.get("sub", "")
            if actor_id:
                logger.info("Extracted actor_id from JWT: %s", actor_id)
                return actor_id
    except Exception as e:
        logger.warning("Failed to extract actor_id from JWT: %s", e)

    return "anonymous"


def _create_agent(session_id: str, actor_id: str):
    """Create the Agent with tools and memory. Called once per session."""
    from strands import Agent
    from strands.models.bedrock import BedrockModel
    from strands_tools.code_interpreter.agent_core_code_interpreter import AgentCoreCodeInterpreter
    from strands_tools.browser.agent_core_browser import AgentCoreBrowser

    model = BedrockModel(model_id=MODEL_ID, region_name=AWS_REGION)

    # --- Tools ---------------------------------------------------------------
    code_interpreter = AgentCoreCodeInterpreter(region=AWS_REGION)
    browser_tool = AgentCoreBrowser(region=AWS_REGION)
    tools = [code_interpreter.code_interpreter, browser_tool.browser]

    # --- Memory --------------------------------------------------------------
    session_manager = None
    if MEMORY_ID:
        from bedrock_agentcore.memory.integrations.strands.config import (
            AgentCoreMemoryConfig, RetrievalConfig,
        )
        from bedrock_agentcore.memory.integrations.strands.session_manager import (
            AgentCoreMemorySessionManager,
        )

        config = AgentCoreMemoryConfig(
            memory_id=MEMORY_ID,
            session_id=session_id,
            actor_id=actor_id,
            retrieval_config={
                "/preferences/{actorId}": RetrievalConfig(top_k=5, relevance_score=0.7),
                "/facts/{actorId}": RetrievalConfig(top_k=10, relevance_score=0.3),
                "/summaries/{actorId}/{sessionId}": RetrievalConfig(top_k=5, relevance_score=0.5),
            },
        )
        session_manager = AgentCoreMemorySessionManager(
            agentcore_memory_config=config, region_name=AWS_REGION,
        )

    # --- Agent ---------------------------------------------------------------
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        **({"session_manager": session_manager} if session_manager else {}),
    )


@app.entrypoint
async def invoke(payload: dict, context: dict = None):
    global _agent

    context = context or {}
    actor_id = _extract_actor_id(context)
    session_id = payload.get("session_id", "default")
    user_message = payload.get(
        "prompt",
        "No prompt found in input. Please send a JSON payload with a 'prompt' key.",
    )

    logger.info("Invocation: actor_id=%s, session_id=%s", actor_id, session_id)

    if _agent is None:
        _agent = _create_agent(session_id, actor_id)

    stream = _agent.stream_async(user_message)
    async for event in stream:
        yield event

    logger.info("Invocation complete: actor_id=%s, session_id=%s", actor_id, session_id)


if __name__ == "__main__":
    app.run()
