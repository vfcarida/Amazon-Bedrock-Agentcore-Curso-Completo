"""Aria V2 -- AI Assistant with Code Interpreter and Browser Tool.

Builds on V1 by adding two managed tools:
- Code Interpreter: sandboxed Python execution for calculations, charts, data analysis
- Browser Tool: headless browser for web searches and real-time information

AgentCore Runtime provisions a dedicated microVM for each session, so
your agent code only ever handles one session at a time.

Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-tools.html
"""

import logging
import os

from bedrock_agentcore.runtime import BedrockAgentCoreApp

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Configuração ---
# Mesmas variáveis de ambiente da V1.
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")

# System Prompt atualizado: Agora descreve as duas novas capacidades do agente
# (execução de código e navegação web) para que o modelo saiba quando usá-las.
SYSTEM_PROMPT = """\
You are Aria, a personal AI assistant. You have the following capabilities:

1. **Code execution** -- You can run Python code for calculations, data analysis, \
charting, file generation, and general-purpose programming. Use the code interpreter \
tool whenever the user needs computation or data processing.

2. **Web browsing** -- You can browse the web to look up current information, verify \
facts, or research topics. Use the browser tool when you need real-time or external data.

Guidelines:
- Be concise and helpful. Prefer structured output (lists, tables, code blocks) when \
it improves clarity.
- When a request is ambiguous, ask a clarifying question rather than guessing.
- Proactively use your tools. If the user asks a factual question you are not confident \
about, browse the web rather than guessing. If they need a calculation, use code.
- Never fabricate tool results. If a tool call fails, tell the user honestly.
"""

app = BedrockAgentCoreApp()

# Criado na primeira execução, e reaproveitado enquanto a microVM estiver viva.
# O Runtime garante uma sessão por microVM, então não precisamos nos preocupar com gestão de múltiplas sessões.
_agent = None


def _create_agent():
    """Create the Agent with tools. Called once per session."""
    from strands import Agent
    from strands.models.bedrock import BedrockModel
    # AgentCoreCodeInterpreter: Ferramenta gerenciada pela AWS que executa código Python
    # em um ambiente isolado (sandbox). Ideal para cálculos, gráficos e análise de dados.
    from strands_tools.code_interpreter.agent_core_code_interpreter import AgentCoreCodeInterpreter
    # AgentCoreBrowser: Ferramenta gerenciada que abre um navegador headless (sem interface gráfica)
    # para acessar páginas web e buscar informações em tempo real.
    from strands_tools.browser.agent_core_browser import AgentCoreBrowser

    model = BedrockModel(model_id=MODEL_ID, region_name=AWS_REGION)

    # Instancia as duas ferramentas gerenciadas do AgentCore Tools.
    # Ambas se comunicam com serviços AWS na mesma região do agente.
    code_interpreter = AgentCoreCodeInterpreter(region=AWS_REGION)
    browser_tool = AgentCoreBrowser(region=AWS_REGION)

    # Monta a lista de ferramentas que o modelo poderá usar.
    # O Strands SDK registra essas ferramentas e permite que o modelo as chame
    # automaticamente quando julgar necessário (via function calling).
    tools = [code_interpreter.code_interpreter, browser_tool.browser]

    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,  # ← Diferença principal da V1: agora o agente tem ferramentas!
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

    # O fluxo é igual ao V1: envia a mensagem e faz streaming da resposta.
    # A diferença é que agora, durante o streaming, o modelo pode decidir
    # chamar ferramentas (code_interpreter ou browser) antes de responder.
    stream = _agent.stream_async(user_message)
    async for event in stream:
        yield event

    logger.info("Invocation complete")


if __name__ == "__main__":
    app.run()
