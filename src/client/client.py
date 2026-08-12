"""Cliente HTTP bruto para o AgentCore Runtime com suporte a OAuth 2.0 / JWT.

Substitui a limitação histórica do boto3.invoke_agent_runtime para autorização M2M,
enviando o token Bearer diretamente no cabeçalho HTTP 'Authorization: Bearer <TOKEN>'
sobre HTTPS e capturando formalmente retornos HTTP 401 Unauthorized e 403 Forbidden.
"""

import json
import logging
from typing import Iterator

import httpx

logger = logging.getLogger(__name__)


class AgentCoreAuthenticationError(Exception):
    """Exceção disparada em falhas de autenticação HTTP 401 Unauthorized."""

    pass


class AgentCoreAuthorizationError(Exception):
    """Exceção disparada em falhas de autorização HTTP 403 Forbidden."""

    pass


class AgentCoreRuntimeClient:
    """Cliente HTTPS nativo para invocação de agentes no AgentCore Runtime."""

    def __init__(self, endpoint_url: str, region: str = "us-east-1"):
        self.endpoint_url = endpoint_url.rstrip("/")
        self.region = region

    def invoke_streaming(
        self,
        prompt: str,
        session_id: str,
        jwt_token: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> Iterator[str]:
        """Invocação HTTPS streaming de borda repassando o token no cabeçalho Authorization.

        Args:
            prompt: Mensagem enviada pelo usuário.
            session_id: ID determinístico da sessão (>= 16 caracteres).
            jwt_token: Token JWT ID/Access de autorização OAuth.
            timeout_seconds: Tempo limite da requisição HTTP em segundos.

        Yields:
            Pedaços do texto retornado via Server-Sent Events (SSE).

        Raises:
            AgentCoreAuthenticationError: Se receber HTTP 401 (token expirado/inválido).
            AgentCoreAuthorizationError: Se receber HTTP 403 (permissão negada/Cedar Policy).
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        if jwt_token:
            clean_token = jwt_token.replace("Bearer ", "").strip()
            headers["Authorization"] = f"Bearer {clean_token}"

        payload = {
            "prompt": prompt,
            "session_id": session_id,
        }

        invocations_url = f"{self.endpoint_url}/invocations"

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                with client.stream(
                    "POST", invocations_url, json=payload, headers=headers
                ) as response:
                    if response.status_code == 401:
                        logger.error(
                            "HTTP 401 Unauthorized: Token JWT ausente ou expirado."
                        )
                        raise AgentCoreAuthenticationError(
                            "Falha de autenticação (HTTP 401): Token JWT inválido ou expirado."
                        )
                    elif response.status_code == 403:
                        logger.error(
                            "HTTP 403 Forbidden: Acesso bloqueado pelas políticas Cedar."
                        )
                        raise AgentCoreAuthorizationError(
                            "Acesso negado (HTTP 403): Operação não autorizada pelas regras de segurança Cedar."
                        )
                    elif response.status_code != 200:
                        logger.error(
                            "Erro no AgentCore Runtime: HTTP %d",
                            response.status_code,
                        )
                        response.raise_for_status()

                    for line in response.iter_lines():
                        line = line.strip()
                        if not line.startswith("data: "):
                            continue
                        try:
                            event_data = json.loads(line[6:])
                            if isinstance(event_data, dict):
                                delta = (
                                    event_data.get("event", {})
                                    .get("contentBlockDelta", {})
                                    .get("delta", {})
                                    .get("text", "")
                                )
                                if not delta:
                                    delta = (
                                        event_data.get("contentBlockDelta", {})
                                        .get("delta", {})
                                        .get("text", "")
                                    )
                                if delta:
                                    yield delta
                        except json.JSONDecodeError:
                            pass

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AgentCoreAuthenticationError(
                    "HTTP 401 Unauthorized: Autenticação negada."
                ) from e
            elif e.response.status_code == 403:
                raise AgentCoreAuthorizationError(
                    "HTTP 403 Forbidden: Autorização negada por Política Cedar."
                ) from e
            raise
