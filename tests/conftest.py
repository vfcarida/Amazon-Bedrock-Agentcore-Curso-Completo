"""Fixtures compartilhadas e emulação de ambiente para a suíte pytest."""

import os
import pytest


@pytest.fixture(autouse=True)
def mock_aws_credentials(monkeypatch):
    """Configura credenciais AWS fictícias para garantir que nenhum teste acesse a rede real."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")


@pytest.fixture
def sample_session_id():
    """Retorna um session_id válido determinístico com no mínimo 16 caracteres."""
    return "session-20260812-143000-a1b2c3d4e5f6"


@pytest.fixture
def sample_jwt_token():
    """Retorna um token JWT simulado para testes de autenticação."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsImVtYWlsIjoid29ya3Nob3BAZXhhbXBsZS5jb20ifQ.signature"
