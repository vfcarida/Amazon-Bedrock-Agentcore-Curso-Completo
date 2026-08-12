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

# --- Configuração ---
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")

# MEMORY_ID: Identificador do recurso de memória no AgentCore.
# É definido como variável de ambiente no deploy do Runtime (Módulo 04).
# Se estiver vazio, o agente funciona normalmente mas sem memória persistente.
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

# Criado na primeira execução, e reaproveitado enquanto a microVM estiver viva.
# O Runtime garante uma sessão por microVM, então não precisamos nos preocupar com gestão de múltiplas sessões.
_agent = None


def _extract_actor_id(context) -> str:
    """Extract the user's actor ID from the JWT in the Authorization header."""
    # O actor_id identifica QUEM é o usuário. Ele vem do campo "sub" (subject)
    # do token JWT enviado no cabeçalho Authorization.
    # A memória usa esse ID para separar as memórias de cada usuário —
    # assim, cada pessoa tem suas próprias preferências e fatos armazenados.
    try:
        headers = getattr(context, "request_headers", None) or {}
        auth_header = headers.get("Authorization", headers.get("authorization", ""))

        if auth_header.startswith("Bearer "):
            import base64
            import json as _json

            # Decodifica o payload do JWT (segunda parte, separada por pontos).
            # Não precisamos verificar a assinatura aqui porque o Runtime já fez isso.
            token = auth_header[7:]
            payload_b64 = token.split(".")[1]
            payload_b64 += "=" * (-len(payload_b64) % 4)  # Padding para base64
            claims = _json.loads(base64.urlsafe_b64decode(payload_b64))

            actor_id = claims.get("sub", "")
            if actor_id:
                logger.info("Extracted actor_id from JWT: %s", actor_id)
                return actor_id
    except Exception as e:
        logger.warning("Failed to extract actor_id from JWT: %s", e)

    # Fallback: Se não conseguir extrair o ID, usa "anonymous".
    return "anonymous"


def _create_agent(session_id: str, actor_id: str):
    """Create the Agent with tools and memory. Called once per session."""
    from strands import Agent
    from strands.models.bedrock import BedrockModel
    from strands_tools.code_interpreter.agent_core_code_interpreter import AgentCoreCodeInterpreter
    from strands_tools.browser.agent_core_browser import AgentCoreBrowser

    model = BedrockModel(model_id=MODEL_ID, region_name=AWS_REGION)

    # --- Tools (Ferramentas) ---------------------------------------------------------------
    # Mesmas ferramentas da V2: Interpretador de Código e Navegador Web.
    code_interpreter = AgentCoreCodeInterpreter(region=AWS_REGION)
    browser_tool = AgentCoreBrowser(region=AWS_REGION)
    tools = [code_interpreter.code_interpreter, browser_tool.browser]

    # --- Memory (Memória) --------------------------------------------------------------
    # Configura a integração com o AgentCore Memory, se o MEMORY_ID estiver definido.
    # O session_manager cuida de:
    # 1. Antes de cada resposta: buscar memórias relevantes e injetá-las no contexto
    # 2. Depois de cada resposta: enviar a conversa para extração de novas memórias
    session_manager = None
    if MEMORY_ID:
        from bedrock_agentcore.memory.integrations.strands.config import (
            AgentCoreMemoryConfig, RetrievalConfig,
        )
        from bedrock_agentcore.memory.integrations.strands.session_manager import (
            AgentCoreMemorySessionManager,
        )

        # retrieval_config: Define quantas memórias buscar de cada namespace
        # e qual o score mínimo de relevância para incluí-las no contexto.
        # - /preferences/{actorId}: Preferências do usuário (ex: "gosta de Python")
        # - /facts/{actorId}: Fatos sobre o usuário (ex: "trabalha na empresa X")
        # - /summaries/{actorId}/{sessionId}: Resumos de conversas passadas
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

    # --- Agent (Agente) ---------------------------------------------------------------
    # O session_manager é passado opcionalmente. Se não tiver MEMORY_ID,
    # o agente funciona igual ao V2 (sem memória).
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        **({"session_manager": session_manager} if session_manager else {}),
    )


def _normalize_session_id(session_id: str) -> str:
    """Garante aderência ao contrato do AgentCore Memory (no mínimo 16 caracteres)."""
    if not session_id or not isinstance(session_id, str):
        return "session-default-16chars"
    clean_id = session_id.strip()
    if len(clean_id) >= 16:
        return clean_id
    import hashlib
    padding = hashlib.sha256(clean_id.encode()).hexdigest()
    needed = 16 - len(clean_id) - 1
    return f"{clean_id}-{padding[:max(needed, 8)]}".ljust(16, "0")


@app.ping
async def ping():
    """Retorna status HealthyBusy para o AgentCore Memory durante operacoes pesadas."""
    return {"status": "HealthyBusy"}


@app.entrypoint
async def invoke(payload: dict, context: dict = None):
    global _agent

    context = context or {}

    # Extrai informações de identidade do usuário antes de criar o agente.
    actor_id = _extract_actor_id(context)
    session_id = _normalize_session_id(payload.get("session_id", "default-session-id"))
    user_message = payload.get(
        "prompt",
        "No prompt found in input. Please send a JSON payload with a 'prompt' key.",
    )

    logger.info("Invocation: actor_id=%s, session_id=%s", actor_id, session_id)

    # O agente é criado com o session_id e actor_id para que a memória
    # saiba de qual usuário e sessão estamos falando.
    if _agent is None:
        _agent = _create_agent(session_id, actor_id)

    stream = _agent.stream_async(user_message)
    async for event in stream:
        yield event

    logger.info("Invocation complete: actor_id=%s, session_id=%s", actor_id, session_id)


if __name__ == "__main__":
    app.run()
