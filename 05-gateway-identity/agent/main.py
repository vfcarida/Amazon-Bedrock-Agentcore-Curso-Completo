"""Aria V4 -- AI Assistant with Gateway & Identity.

Builds on V3 by adding AgentCore Gateway for API access:
- MCP client connects to Gateway endpoint
- JWT is forwarded from the user's request to Gateway (CUSTOM_JWT auth)
- Gateway auto-discovers tools from the connected Task Management API
- Identity flow: User JWT -> Runtime -> Gateway -> Cedar Policy -> Target API

AgentCore Runtime provisions a dedicated microVM for each session, so
your agent code only ever handles one session at a time.

Docs:
  Gateway: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-gateway.html
  Identity: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-identity.html
"""

import logging
import os

from bedrock_agentcore.runtime import BedrockAgentCoreApp

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Configuração ---
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
MEMORY_ID = os.environ.get("MEMORY_ID", "")

# GATEWAY_ENDPOINT: URL do Gateway MCP criado no Módulo 05.
# O agente se conecta a este endpoint como um cliente MCP para descobrir
# e usar as ferramentas da API de Tarefas (list, create, update, delete).
GATEWAY_ENDPOINT = os.environ.get("GATEWAY_ENDPOINT", "")

# System Prompt atualizado: Agora inclui a capacidade de gerenciar tarefas
# e instrui o modelo a oferecer proativamente a criação de tarefas.
SYSTEM_PROMPT = """\
You are Aria, a personal AI assistant. You have the following capabilities:

1. **Code execution** -- Run Python code for calculations, data analysis, and charting.

2. **Web browsing** -- Browse the web to look up current information.

3. **Task management** -- Create, list, update, and delete tasks through the \
connected Task Management API. Help the user stay organized.

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
    """Extract the JWT from the payload or context headers.

    Checks two sources:
    1. payload["authorization"] -- for SigV4 invocations that pass the JWT in the request body
    2. context.request_headers["Authorization"] -- for JWT-authenticated Runtime invocations
    """
    # IMPORTANTE: O JWT precisa ser repassado para o Gateway para que:
    # 1. O Gateway saiba quem é o usuário (autenticação)
    # 2. O Cedar Policy possa avaliar as permissões desse usuário (autorização)
    # 3. A API de Tarefas saiba de quem são as tarefas
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
    # Mesmo mecanismo da V3, mas agora recebe o header já extraído
    # em vez de acessar o context diretamente.
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
    """Create the Agent with tools, gateway, and memory. Called once per session."""
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
    # MCP (Model Context Protocol): Protocolo aberto que permite que modelos de IA
    # descubram e usem ferramentas automaticamente. O Gateway expõe a API de Tarefas
    # como um servidor MCP, e o agente se conecta como cliente.
    #
    # Fluxo de identidade (JWT forwarding):
    # Usuário → Frontend → Runtime (JWT no header) → Agente → Gateway (JWT repassado) → API de Tarefas
    if GATEWAY_ENDPOINT:
        import httpx
        from strands.tools.mcp import MCPClient
        from mcp.client.streamable_http import streamable_http_client

        # Repassa o JWT do usuário no cabeçalho Authorization do cliente MCP.
        # Isso garante que o Gateway sabe quem é o usuário e pode aplicar
        # as políticas Cedar corretamente.
        gateway_headers = {}
        if auth_header.startswith("Bearer "):
            gateway_headers["Authorization"] = auth_header

        _gw_headers = dict(gateway_headers)

        # MCPClient: Cria um cliente MCP que se conecta ao Gateway via HTTP.
        # O Gateway retorna a lista de ferramentas disponíveis (list_tasks, create_task, etc.)
        # e o Strands SDK as registra automaticamente para o modelo usar.
        gateway_mcp = MCPClient(lambda: streamable_http_client(
            url=GATEWAY_ENDPOINT,
            http_client=httpx.AsyncClient(headers=_gw_headers),
        ))
        tools.append(gateway_mcp)

    # --- Memory (Memória) --------------------------------------------------------------
    # Mesma configuração da V3 — não mudou nada aqui.
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


@app.entrypoint
async def invoke(payload: dict, context: dict = None):
    global _agent

    context = context or {}

    # Extrai o JWT e o actor_id para autenticação e identidade.
    auth_header = _extract_jwt(payload, context)
    actor_id = _extract_actor_id(auth_header)
    session_id = payload.get("session_id", "default")
    user_message = payload.get(
        "prompt",
        "No prompt found in input. Please send a JSON payload with a 'prompt' key.",
    )

    logger.info("Invocation: actor_id=%s, session_id=%s", actor_id, session_id)

    if _agent is None:
        # O auth_header é passado para o _create_agent para que o cliente MCP
        # do Gateway receba o JWT do usuário.
        _agent = _create_agent(session_id, actor_id, auth_header)

    stream = _agent.stream_async(user_message)
    async for event in stream:
        yield event

    logger.info("Invocation complete: actor_id=%s, session_id=%s", actor_id, session_id)


if __name__ == "__main__":
    app.run()
