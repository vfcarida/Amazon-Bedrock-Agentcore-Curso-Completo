"""Pacote de agentes do Amazon Bedrock AgentCore."""

from .gateway_agent import app as gateway_app
from .memory_agent import app as memory_app
from .observability_agent import app as observability_app
from .runtime_agent import app as runtime_app
from .tools_agent import app as tools_app

__all__ = [
    "runtime_app",
    "tools_app",
    "memory_app",
    "gateway_app",
    "observability_app",
]
