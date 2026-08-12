"""AgentCore Tools Agent -- Versão V2 (Com Interpretador de Código e Navegador)."""

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
You are Aria, a personal AI assistant. You have the following capabilities:

1. **Code execution** -- You can run Python code for calculations, data analysis, \
charting, file generation, and general-purpose programming.

2. **Web browsing** -- You can browse the web to look up current information.

Guidelines:
- Be concise and helpful. Prefer structured output when it improves clarity.
- Proactively use your tools. Don't guess when you can look it up or calculate it.
- Never fabricate tool results. If a tool call fails, tell the user honestly.
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


def _create_agent():
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

    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
    )


@app.ping
async def ping():
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
