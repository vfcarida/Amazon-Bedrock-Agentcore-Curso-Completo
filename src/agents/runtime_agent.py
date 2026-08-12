"""AgentCore Runtime Agent -- Versão V1 (Básica)."""

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

SYSTEM_PROMPT = """\
You are Aria, a personal AI assistant. You are helpful, concise, and friendly.

Guidelines:
- Be concise and helpful. Prefer structured output (lists, tables, code blocks) when \
it improves clarity.
- When a request is ambiguous, ask a clarifying question rather than guessing.
- Never fabricate information. If you don't know something, say so honestly.
"""

app = BedrockAgentCoreApp()
_agent = None


def _normalize_session_id(session_id: str) -> str:
    """Garante aderência contratual exigindo no mínimo 16 caracteres."""
    if not session_id or not isinstance(session_id, str):
        return "session-default-16chars"
    clean_id = session_id.strip()
    if len(clean_id) >= 16:
        return clean_id
    padding = hashlib.sha256(clean_id.encode()).hexdigest()
    needed = 16 - len(clean_id) - 1
    return f"{clean_id}-{padding[:max(needed, 8)]}".ljust(16, "0")


def _create_agent():
    """Cria a instância do agente Strands."""
    from strands import Agent
    from strands.models.bedrock import BedrockModel

    model = BedrockModel(model_id=MODEL_ID, region_name=AWS_REGION)
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
    )


@app.ping
async def ping():
    """Terminal GET /ping: Retorna status HealthyBusy durante tarefas de background."""
    return {"status": "HealthyBusy"}


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
