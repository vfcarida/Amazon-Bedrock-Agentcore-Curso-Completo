"""Testes unitários de validação do contrato de servidor GET /ping (HealthyBusy)."""

import sys
import types
import pytest

# Emulação de mock para a biblioteca bedrock_agentcore caso não esteja instalada no ambiente local
if "bedrock_agentcore" not in sys.modules:
    mock_bedrock = types.ModuleType("bedrock_agentcore")
    mock_runtime = types.ModuleType("bedrock_agentcore.runtime")

    class MockBedrockAgentCoreApp:
        def __init__(self):
            pass

        def entrypoint(self, func):
            return func

        def ping(self, func):
            return func

        def run(self):
            pass

    mock_runtime.BedrockAgentCoreApp = MockBedrockAgentCoreApp
    mock_bedrock.runtime = mock_runtime
    sys.modules["bedrock_agentcore"] = mock_bedrock
    sys.modules["bedrock_agentcore.runtime"] = mock_runtime


@pytest.mark.asyncio
async def test_ping_contract_returns_healthy_busy():
    """Valida se as funções de ping cadastradas nos agentes retornam status HealthyBusy."""
    import importlib.util
    from pathlib import Path

    agent_path = (
        Path(__file__).resolve().parent.parent
        / "02-runtime"
        / "agent"
        / "main.py"
    )
    spec = importlib.util.spec_from_file_location(
        "runtime_agent_main", agent_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    ping_result = await module.ping()

    assert isinstance(ping_result, dict)
    assert "status" in ping_result
    assert ping_result["status"] == "HealthyBusy"
