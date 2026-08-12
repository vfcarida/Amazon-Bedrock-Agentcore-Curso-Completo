"""Testes unitários com mocks para o cliente HTTPS AgentCoreRuntimeClient."""

from unittest.mock import MagicMock, patch

import pytest
from src.client.client import (
    AgentCoreAuthenticationError,
    AgentCoreAuthorizationError,
    AgentCoreRuntimeClient,
)


def test_client_headers_and_bearer_token_injection(
    sample_session_id, sample_jwt_token
):
    """Valida se o cabeçalho Authorization: Bearer <TOKEN> é corretamente inserido."""
    client = AgentCoreRuntimeClient(endpoint_url="https://mock-agentcore.aws")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = [
        'data: {"event": {"contentBlockDelta": {"delta": {"text": "Hello world"}}}}'
    ]

    with patch("httpx.Client") as mock_httpx_cls:
        mock_client = MagicMock()
        mock_httpx_cls.return_value.__enter__.return_value = mock_client
        mock_stream_ctx = MagicMock()
        mock_stream_ctx.__enter__.return_value = mock_response
        mock_client.stream.return_value = mock_stream_ctx

        generator = client.invoke_streaming(
            prompt="Hi",
            session_id=sample_session_id,
            jwt_token=sample_jwt_token,
        )
        chunks = list(generator)

        assert chunks == ["Hello world"]
        mock_client.stream.assert_called_once()
        args, kwargs = mock_client.stream.call_args
        assert kwargs["headers"]["Authorization"] == f"Bearer {sample_jwt_token}"
        assert kwargs["json"]["session_id"] == sample_session_id


def test_client_handles_http_401_unauthorized(sample_session_id):
    """Valida se o cliente dispara AgentCoreAuthenticationError em respostas HTTP 401."""
    client = AgentCoreRuntimeClient(endpoint_url="https://mock-agentcore.aws")

    mock_response = MagicMock()
    mock_response.status_code = 401

    with patch("httpx.Client") as mock_httpx_cls:
        mock_client = MagicMock()
        mock_httpx_cls.return_value.__enter__.return_value = mock_client
        mock_stream_ctx = MagicMock()
        mock_stream_ctx.__enter__.return_value = mock_response
        mock_client.stream.return_value = mock_stream_ctx

        with pytest.raises(AgentCoreAuthenticationError):
            list(
                client.invoke_streaming(
                    prompt="Hi",
                    session_id=sample_session_id,
                    jwt_token="invalid-token",
                )
            )


def test_client_handles_http_403_forbidden(sample_session_id):
    """Valida se o cliente dispara AgentCoreAuthorizationError em respostas HTTP 403."""
    client = AgentCoreRuntimeClient(endpoint_url="https://mock-agentcore.aws")

    mock_response = MagicMock()
    mock_response.status_code = 403

    with patch("httpx.Client") as mock_httpx_cls:
        mock_client = MagicMock()
        mock_httpx_cls.return_value.__enter__.return_value = mock_client
        mock_stream_ctx = MagicMock()
        mock_stream_ctx.__enter__.return_value = mock_response
        mock_client.stream.return_value = mock_stream_ctx

        with pytest.raises(AgentCoreAuthorizationError):
            list(
                client.invoke_streaming(
                    prompt="Unauthorized action",
                    session_id=sample_session_id,
                    jwt_token="valid-token",
                )
            )
