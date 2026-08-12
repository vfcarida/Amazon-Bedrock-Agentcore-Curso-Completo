"""Módulo de cliente e gestão de sessão para o Amazon Bedrock AgentCore."""

from .session import generate_deterministic_session_id

__all__ = ["generate_deterministic_session_id"]
