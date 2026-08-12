"""AgentCore Memory Agent -- Versão V3 (Com Memória Persistente)."""

import hashlib
import logging
import os

from bedrock_agentcore.runtime import BedrockAgentCoreApp

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get(
    "MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
)
MEMORY_ID = os.environ.get("MEMORY_ID", "")

SYSTEM_PROMPT = """\
You are Aria, a personal AI assistant. You have memory of user preferences and facts.
Guidelines:
- Be concise and helpful.
- Reference user preferences and facts stored in AgentCore Memory.
"""

app = BedrockAgentCoreApp()
_agent = None


def _normalize_session_id(session_id: str) -> str:
    if not session_id or not isinstance(session_id, str):
        return "session-default-16chars"
    clean_id = session_id.strip()
    if len(clean_id) >= 16:
        return clean_id
    padding = hashlib.sha256(clean_id.encode()).hexdigest()
    needed = 16 - len(clean_id) - 1
    return f"{clean_id}-{padding[:max(needed, 8)]}".ljust(16, "0")


def _extract_actor_id(context) -> str:
    try:
        headers = getattr(context, "request_headers", None) or {}
        auth_header = headers.get(
            "Authorization", headers.get("authorization", "")
        )
        if auth_header.startswith("Bearer "):
            import base64
            import json as _json

            token = auth_header[7:]
            payload_b64 = token.split(".")[1]
            payload_b64 += "=" * (-len(payload_b64) % 4)
            claims = _json.loads(base64.urlsafe_b64decode(payload_b64))
            return claims.get("sub", "anonymous")
    except Exception:
        pass
    return "anonymous"


def _create_agent(session_id: str, actor_id: str):
    from strands import Agent
    from strands.models.bedrock import BedrockModel
    from strands_tools.browser.agent_core_browser import AgentCoreBrowser
    from strands_tools.code_interpreter.agent_core_code_interpreter import (
        AgentCoreCodeInterpreter,
    )

    model = BedrockModel(model_id=MODEL_ID, region_name=AWS_REGION)
    code_interpreter = AgentCoreCodeInterpreter(region=AWS_REGION)
    browser_tool = AgentCoreBrowser(region=AWS_REGION)
    tools = [code_interpreter.code_interpreter, browser_tool.browser]

    session_manager = None
    if MEMORY_ID:
        from bedrock_agentcore.memory.integrations.strands.config import (
            AgentCoreMemoryConfig,
            RetrievalConfig,
        )
        from bedrock_agentcore.memory.integrations.strands.session_manager import (
            AgentCoreMemorySessionManager,
        )

        config = AgentCoreMemoryConfig(
            memory_id=MEMORY_ID,
            session_id=session_id,
            actor_id=actor_id,
            retrieval_config={
                "/preferences/{actorId}": RetrievalConfig(
                    top_k=5, relevance_score=0.7
                ),
                "/facts/{actorId}": RetrievalConfig(
                    top_k=10, relevance_score=0.3
                ),
                "/summaries/{actorId}/{sessionId}": RetrievalConfig(
                    top_k=5, relevance_score=0.5
                ),
            },
        )
        session_manager = AgentCoreMemorySessionManager(
            agentcore_memory_config=config, region_name=AWS_REGION
        )

    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        **({"session_manager": session_manager} if session_manager else {}),
    )


@app.ping
async def ping():
    return {"status": "HealthyBusy"}


@app.entrypoint
async def invoke(payload: dict, context: dict = None):
    global _agent

    context = context or {}
    actor_id = _extract_actor_id(context)
    session_id = _normalize_session_id(
        payload.get("session_id", "default-session-id")
    )
    user_message = payload.get("prompt", "")

    if _agent is None:
        _agent = _create_agent(session_id, actor_id)

    stream = _agent.stream_async(user_message)
    async for event in stream:
        yield event


if __name__ == "__main__":
    app.run()
