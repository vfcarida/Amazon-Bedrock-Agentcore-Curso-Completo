"""Aria V5 -- Production AI Assistant with Full Observability.

The final version of Aria. Builds on V4 by adding OpenTelemetry tracing
for full observability. Traces flow to CloudWatch via AgentCore's built-in
OTel integration.

This is the same agent that runs in production -- all 9 AgentCore services
are now active: Runtime, Code Interpreter, Browser Tool, Memory, Gateway,
Identity, Policy (at Gateway level), Observability, and Evaluations.

AgentCore Runtime provisions a dedicated microVM for each session, so
your agent code only ever handles one session at a time. The Agent is
created once on first invocation and reused for subsequent invocations
within the session. AgentCore Memory provides cross-session recall of
preferences, facts, and summaries.

Docs:
  Observability: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-observability.html
  Evaluations: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-evaluations.html
"""

import logging
import os

from bedrock_agentcore.runtime import BedrockAgentCoreApp

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Configuração ---
# Na V5, as variáveis de ambiente são as mesmas da V4.
# A diferença está no deploy: o entrypoint é envolvido pelo opentelemetry-instrument,
# que automaticamente coleta traces de todas as chamadas HTTP, SDK e ferramentas.
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
MEMORY_ID = os.environ.get("MEMORY_ID", "")
GATEWAY_ENDPOINT = os.environ.get("GATEWAY_ENDPOINT", "")

SYSTEM_PROMPT = """\
You are Aria, a personal AI assistant. You have the following capabilities:

1. **Code execution** -- Run Python code for calculations, data analysis, and charting.

2. **Web browsing** -- Browse the web to look up current information.

3. **Task management** -- Create, list, update, and delete tasks through the \
connected Task Management API.

4. **Memory** -- You remember user preferences, facts, and conversation history \
across sessions.

Guidelines:
- Be concise and helpful. Prefer structured output when it improves clarity.
- Proactively use your tools. Don't guess when you can look it up or calculate it.
- Reference what you remember about the user when relevant.
- When users mention things they need to do, proactively offer to create tasks.
- Never fabricate tool results or memories.
"""

app = BedrockAgentCoreApp()

# Criado na primeira execução, e reaproveitado enquanto a microVM estiver viva.
# O Runtime garante uma sessão por microVM, então não precisamos nos preocupar com gestão de múltiplas sessões.
_agent = None


def _extract_jwt(payload: dict, context) -> str:
    """Extract the JWT from the payload or context headers."""
    # Mesmo mecanismo da V4: tenta extrair o JWT do payload ou dos headers.
    auth_header = payload.get("authorization", "")
    if not auth_header:
        try:
            headers = getattr(context, "request_headers", None) or {}
            auth_header = headers.get("Authorization", headers.get("authorization", ""))
        except Exception:
            pass
    return auth_header


def _extract_actor_id(auth_header: str) -> str:
    """Extract the user's actor ID (sub claim) from a JWT."""
    try:
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


def _create_agent(session_id: str, actor_id: str, auth_header: str):
    """Create the Agent with all tools and integrations. Called once per session.

    Heavy imports are deferred to first call so module-level init stays
    within the Runtime cold-start window.
    """
    # Lazy imports: Carregamos as dependências pesadas apenas na primeira chamada.
    # Isso reduz o tempo de cold start da microVM do Runtime.
    from strands import Agent
    from strands.models.bedrock import BedrockModel
    from strands_tools.code_interpreter.agent_core_code_interpreter import AgentCoreCodeInterpreter
    from strands_tools.browser.agent_core_browser import AgentCoreBrowser

    model = BedrockModel(model_id=MODEL_ID, region_name=AWS_REGION)

    # --- Tools (Ferramentas) ---------------------------------------------------------------
    code_interpreter = AgentCoreCodeInterpreter(region=AWS_REGION)
    browser_tool = AgentCoreBrowser(region=AWS_REGION)
    tools = [code_interpreter.code_interpreter, browser_tool.browser]

    # --- Cliente MCP do Gateway --------------------------------------------------
    # Mesmo código da V4: conecta ao Gateway e repassa o JWT.
    if GATEWAY_ENDPOINT:
        import httpx
        from strands.tools.mcp import MCPClient
        from mcp.client.streamable_http import streamable_http_client

        gateway_headers = {}
        if auth_header.startswith("Bearer "):
            gateway_headers["Authorization"] = auth_header

        _gw_headers = dict(gateway_headers)

        gateway_mcp = MCPClient(lambda: streamable_http_client(
            url=GATEWAY_ENDPOINT,
            http_client=httpx.AsyncClient(headers=_gw_headers),
        ))
        tools.append(gateway_mcp)

    # --- Memory (Memória) --------------------------------------------------------------
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

    # --- Agent (Agente) ---------------------------------------------------------------
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        **({"session_manager": session_manager} if session_manager else {}),
    )


def _normalize_session_id(session_id: str) -> str:
    """Garante aderência ao contrato do AgentCore Memory/Observability (mínimo 16 caracteres)."""
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
    """Retorna status HealthyBusy para o AgentCore em tarefas de observabilidade."""
    return {"status": "HealthyBusy"}


@app.entrypoint
async def invoke(payload: dict, context: dict = None):
    global _agent

    context = context or {}
    auth_header = _extract_jwt(payload, context)
    actor_id = _extract_actor_id(auth_header)
    session_id = _normalize_session_id(payload.get("session_id", "default-session-id"))
    user_message = payload.get(
        "prompt",
        "No prompt found in input. Please send a JSON payload with a 'prompt' key.",
    )

    logger.info("Invocation: actor_id=%s, session_id=%s", actor_id, session_id)

    # DIFERENÇA PRINCIPAL DA V5: Bloco try/except/finally para produção.
    # Em produção, erros não podem "sumir" silenciosamente. Aqui garantimos que:
    # 1. Erros são logados com stack trace completo (logger.exception)
    # 2. A exceção é re-lançada para que o Runtime retorne erro ao cliente
    # 3. O log de conclusão sempre é registrado (finally), mesmo em caso de erro
    #
    # O OpenTelemetry (ativado via entrypoint wrapper) captura automaticamente
    # todos os traces e os envia para o CloudWatch/X-Ray, permitindo debug
    # e monitoramento de performance em tempo real.
    try:
        if _agent is None:
            _agent = _create_agent(session_id, actor_id, auth_header)

        stream = _agent.stream_async(user_message)
        async for event in stream:
            yield event
    except Exception:
        logger.exception("Agent invocation failed: actor_id=%s, session_id=%s", actor_id, session_id)
        raise
    finally:
        logger.info("Invocation complete: actor_id=%s, session_id=%s", actor_id, session_id)


if __name__ == "__main__":
    app.run()
