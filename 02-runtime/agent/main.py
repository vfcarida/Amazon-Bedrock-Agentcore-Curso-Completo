"""Aria V1 -- Basic AI Assistant on AgentCore Runtime.

This is the simplest version of Aria: a conversational agent deployed to
AgentCore Runtime with streaming responses. No tools, no memory, no gateway.

AgentCore Runtime provisions a dedicated microVM for each session, so
your agent code only ever handles one session at a time. Conversation
history is preserved automatically because the Agent object lives in
the process for the lifetime of the microVM.

Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-runtime.html
"""

import logging
import os

from bedrock_agentcore.runtime import BedrockAgentCoreApp

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")

SYSTEM_PROMPT = """\
You are Aria, a personal AI assistant. You are helpful, concise, and friendly.

Guidelines:
- Be concise and helpful. Prefer structured output (lists, tables, code blocks) when \
it improves clarity.
- When a request is ambiguous, ask a clarifying question rather than guessing.
- Never fabricate information. If you don't know something, say so honestly.
"""

# ---------------------------------------------------------------------------
# Runtime app
# ---------------------------------------------------------------------------

app = BedrockAgentCoreApp()

# The Agent is created on first invocation and reused for subsequent
# invocations within the same session. Runtime guarantees that each
# session runs in its own microVM, so there is only ever one session here.
_agent = None


def _create_agent():
    """Create the Agent. Called once per session (i.e. once per microVM)."""
    from strands import Agent
    from strands.models.bedrock import BedrockModel

    model = BedrockModel(model_id=MODEL_ID, region_name=AWS_REGION)

    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
    )


@app.entrypoint
async def invoke(payload: dict, context: dict = None):
    global _agent

    user_message = payload.get(
        "prompt",
        "No prompt found in input. Please send a JSON payload with a 'prompt' key.",
    )

    logger.info("Invocation: prompt_length=%d", len(user_message))

    if _agent is None:
        _agent = _create_agent()

    stream = _agent.stream_async(user_message)
    async for event in stream:
        yield event

    logger.info("Invocation complete")


if __name__ == "__main__":
    app.run()
