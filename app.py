#!/usr/bin/env python3
"""Aplicação Frontend Streamlit Pronta para Produção -- Interface da Aria (AgentCore).

Esta aplicação resolve estruturalmente o conflito entre o loop de eventos assíncrono
do gerador do AgentCore Runtime (stream_async) e o modelo de execução síncrono do Streamlit.

Padrões de Engenharia Aplicados:
1. Eliminação de asyncio.run() bloqueante na thread principal.
2. Padrão de Pré-layout com st.empty() para renderização sem cintilação.
3. Deslocamento da invocação de rede para thread secundária via ThreadPoolExecutor.
4. Ancoragem do contexto da sessão gráfica utilizando add_script_run_ctx.
5. Processamento iterativo seguro de Server-Sent Events (SSE) via st.write_stream.
"""

import codecs
import json
import queue
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import boto3
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# Adiciona o diretório do projeto ao PATH
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from shared import utils

# ---------------------------------------------------------------------------
# Configuração da Página e Estilização CSS Moderna
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Aria - AgentCore AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Função Auxiliar de Invocação em Thread Paralela com Contexto Ancorado
# ---------------------------------------------------------------------------


def _worker_invoke_agent(
    runtime_arn: str,
    session_id: str,
    prompt: str,
    jwt_token: str | None,
    region: str,
    out_queue: queue.Queue,
    script_ctx,
):
    """Executa a chamada HTTP/SSE ao AgentCore Runtime em uma thread secundária.

    Ancora o contexto gráfico da sessão via add_script_run_ctx para compartilhar
    estado com a thread principal do Streamlit com total segurança de concorrência.
    """
    if script_ctx is not None:
        add_script_run_ctx(ctx=script_ctx)

    try:
        client = boto3.client("bedrock-agentcore", region_name=region)
        payload = {"prompt": prompt, "session_id": session_id}
        if jwt_token:
            payload["authorization"] = f"Bearer {jwt_token}"

        response = client.invoke_agent_runtime(
            agentRuntimeArn=runtime_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(payload).encode(),
        )

        stream = response["response"]
        buffer = ""
        decoder = codecs.getincrementaldecoder("utf-8")("replace")

        for chunk in stream.iter_chunks(chunk_size=1024):
            buffer += decoder.decode(chunk, final=False)
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line.startswith("data: "):
                    continue
                try:
                    event = json.loads(line[6:])
                    if not isinstance(event, dict):
                        continue
                    if event.get("error"):
                        out_queue.put(f"\n❌ Erro: {event['error']}")
                        continue
                    delta = (
                        event.get("event", {})
                        .get("contentBlockDelta", {})
                        .get("delta", {})
                        .get("text", "")
                    )
                    if not delta:
                        delta = (
                            event.get("contentBlockDelta", {})
                            .get("delta", {})
                            .get("text", "")
                        )
                    if delta:
                        out_queue.put(delta)
                except Exception:
                    pass

        buffer += decoder.decode(b"", final=True)
        if buffer.strip().startswith("data: "):
            try:
                event = json.loads(buffer.strip()[6:])
                if isinstance(event, dict):
                    delta = (
                        event.get("event", {})
                        .get("contentBlockDelta", {})
                        .get("delta", {})
                        .get("text", "")
                    )
                    if not delta:
                        delta = (
                            event.get("contentBlockDelta", {})
                            .get("delta", {})
                            .get("text", "")
                        )
                    if delta:
                        out_queue.put(delta)
            except Exception:
                pass

    except Exception as e:
        out_queue.put(f"\n❌ Erro de comunicação com o AgentCore Runtime: {str(e)}")
    finally:
        out_queue.put(None)  # Sinal de término do stream


def stream_agent_response(
    runtime_arn: str,
    session_id: str,
    prompt: str,
    jwt_token: str | None,
    region: str,
):
    """Gerador síncrono que consome os pedaços transmitidos pela thread secundária.

    Proporciona o fluxo de dados para a diretiva st.write_stream do Streamlit.
    """
    out_queue = queue.Queue()
    script_ctx = get_script_run_ctx()

    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(
            _worker_invoke_agent,
            runtime_arn,
            session_id,
            prompt,
            jwt_token,
            region,
            out_queue,
            script_ctx,
        )

        while True:
            chunk = out_queue.get()
            if chunk is None:
                break
            yield chunk


# ---------------------------------------------------------------------------
# Gerenciamento de Estado da Sessão Streamlit
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session-{uuid.uuid4().hex[:16]}"

# ---------------------------------------------------------------------------
# Sidebar (Configurações & Status)
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("⚙️ Configurações")

    region = st.text_input("Região AWS", value=utils.get_region())

    runtime_config = utils.load_config("runtime") or {}
    default_runtime_arn = runtime_config.get("runtime_arn", "")
    runtime_arn = st.text_input("AgentCore Runtime ARN", value=default_runtime_arn)

    auth_mode = st.radio(
        "Modo de Autenticação", ["IAM (Direto)", "OAuth (JWT / Cognito)"]
    )

    jwt_token = None
    if auth_mode == "OAuth (JWT / Cognito)":
        jwt_token = st.text_input(
            "JWT ID Token",
            type="password",
            help="Insira o token JWT de autenticação",
        )

    st.divider()
    st.markdown(f"**Session ID**: `{st.session_state.session_id}`")

    if st.button("Nova Sessão", use_container_width=True):
        st.session_state.session_id = f"session-{uuid.uuid4().hex[:16]}"
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# Área Principal do Chat
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="main-header">🤖 Aria — Assistente Virtual AgentCore</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Demonstrador de Engenharia com Amazon Bedrock AgentCore Runtime, Memory & Gateway</div>',
    unsafe_allow_html=True,
)

# Renderiza histórico de mensagens armazenado na sessão
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Entrada do usuário
if prompt := st.chat_input("Digite sua mensagem para a Aria..."):
    if not runtime_arn:
        st.error("Por favor, informe um AgentCore Runtime ARN válido na barra lateral.")
    else:
        # Adiciona mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # --- Padrão de Pré-layout ---
        # Instancia objeto visual vazio na interface antes de iniciar o processamento pesado
        with st.chat_message("assistant"):
            response_placeholder = st.empty()

            # Utiliza st.write_stream consumindo o gerador da thread paralela
            full_response = response_placeholder.write_stream(
                stream_agent_response(
                    runtime_arn=runtime_arn,
                    session_id=st.session_state.session_id,
                    prompt=prompt,
                    jwt_token=jwt_token,
                    region=region,
                )
            )

        # Armazena resposta completa do assistente no histórico
        if full_response:
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
