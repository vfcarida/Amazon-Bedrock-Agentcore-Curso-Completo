"""Aria V1 -- Basic AI Assistant on AgentCore Runtime.

This is the simplest version of Aria: a conversational agent deployed to
AgentCore Runtime with streaming responses. No tools, no memory, no gateway.

AgentCore Runtime provisions a dedicated microVM for each session, so
your agent code only ever handles one session at a time. Conversation
history is preserved automatically because the Agent object lives in
the process for the lifetime of the microVM.

Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-runtime.html
"""

# --- Imports ---
# logging: Para registrar mensagens de log (info, warning, error) durante a execução do agente.
# os: Para acessar variáveis de ambiente do sistema (como região AWS e modelo a ser usado).
import logging
import os

# BedrockAgentCoreApp: Classe principal do SDK do AgentCore Runtime.
# Ela cuida de toda a comunicação com a infraestrutura da AWS (receber requisições,
# enviar respostas em streaming, gerenciar o ciclo de vida da microVM).
from bedrock_agentcore.runtime import BedrockAgentCoreApp

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
# Lê a região e o modelo a partir de variáveis de ambiente.
# Isso permite trocar o modelo ou região sem alterar o código —
# basta mudar as variáveis de ambiente no deploy do Runtime.

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")

# System Prompt: Define a "personalidade" e as regras de comportamento da Aria.
# O modelo lê este texto antes de cada conversa e usa como guia para suas respostas.
SYSTEM_PROMPT = """\
You are Aria, a personal AI assistant. You are helpful, concise, and friendly.

Guidelines:
- Be concise and helpful. Prefer structured output (lists, tables, code blocks) when \
it improves clarity.
- When a request is ambiguous, ask a clarifying question rather than guessing.
- Never fabricate information. If you don't know something, say so honestly.
"""

# ---------------------------------------------------------------------------
# App do Runtime
# ---------------------------------------------------------------------------
# Cria a instância do aplicativo AgentCore Runtime.
# Esta é a ponte entre o seu código Python e a infraestrutura da AWS.

app = BedrockAgentCoreApp()

# O Agente é criado na primeira vez que é chamado e reutilizado nas próximas
# chamadas da mesma sessão. O Runtime garante que cada
# sessão rode isolada na sua própria microVM, então só existe uma sessão rodando aqui.
_agent = None


def _create_agent():
    """Create the Agent. Called once per session (i.e. once per microVM)."""
    # Importações "atrasadas" (lazy imports): só carregamos o Strands e o modelo do Bedrock
    # quando realmente precisamos. Isso acelera o tempo de inicialização da microVM.
    from strands import Agent
    from strands.models.bedrock import BedrockModel

    # BedrockModel: Wrapper que conecta o Strands SDK ao Amazon Bedrock.
    # Ele faz as chamadas de API ao serviço de modelos da AWS.
    model = BedrockModel(model_id=MODEL_ID, region_name=AWS_REGION)

    # Cria o agente com o modelo e o system prompt.
    # Nesta V1, o agente não tem ferramentas — ele só conversa.
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
    )


# @app.entrypoint: Decorador que marca esta função como o ponto de entrada
# do agente. O Runtime chama esta função toda vez que o agente recebe uma
# mensagem do usuário.
@app.entrypoint
async def invoke(payload: dict, context: dict = None):
    global _agent

    # Extrai a mensagem do usuário do payload JSON recebido.
    # Se não houver campo "prompt", usa uma mensagem de erro padrão.
    user_message = payload.get(
        "prompt",
        "No prompt found in input. Please send a JSON payload with a 'prompt' key.",
    )

    logger.info("Invocation: prompt_length=%d", len(user_message))

    # Cria o agente apenas uma vez (primeira invocação).
    # Nas próximas chamadas, reutiliza o mesmo objeto — assim o histórico
    # de conversa é mantido automaticamente pelo Strands SDK.
    if _agent is None:
        _agent = _create_agent()

    # stream_async: Envia a mensagem para o modelo e retorna um iterador assíncrono.
    # Cada "event" é um pedaço da resposta (token) que o modelo vai gerando.
    # O "yield" repassa cada pedaço em tempo real de volta para o usuário (streaming).
    stream = _agent.stream_async(user_message)
    async for event in stream:
        yield event

    logger.info("Invocation complete")


# Ponto de entrada quando o arquivo é executado diretamente.
# app.run() inicia o servidor HTTP local que o Runtime usa para se comunicar com o agente.
if __name__ == "__main__":
    app.run()
