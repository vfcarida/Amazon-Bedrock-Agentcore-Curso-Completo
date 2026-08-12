"""Instrumentação nativa OpenTelemetry para rastreamento de LLMs no AgentCore.

Permite que os painéis do CloudWatch Transaction Search interpretem a latência,
métricas de tokens e spans de tempo das invocações dos modelos e chamadas de ferramentas.
"""

import asyncio
import functools
import logging
from typing import Any, Callable

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Tracer

logger = logging.getLogger(__name__)

_TRACER_NAME = "aria.agentcore.telemetry"
_tracer_initialized = False


def setup_telemetry(service_name: str = "aria-agentcore-runtime") -> TracerProvider:
    """Configura o provedor de traces OpenTelemetry para o AgentCore Runtime.

    Args:
        service_name: Nome do serviço enviado nas métricas do CloudWatch.

    Returns:
        Instância do TracerProvider configurada.
    """
    global _tracer_initialized
    provider = trace.get_tracer_provider()

    if not _tracer_initialized:
        if not isinstance(provider, TracerProvider):
            provider = TracerProvider()
            trace.set_tracer_provider(provider)

        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        _tracer_initialized = True
        logger.info(
            "OpenTelemetry inicializado com sucesso para o serviço: %s",
            service_name,
        )

    return provider


def get_tracer() -> Tracer:
    """Retorna a instância do Tracer configurado."""
    return trace.get_tracer(_TRACER_NAME)


def trace_span(name: str):
    """Decorador para instrumentar funções Python com spans OpenTelemetry.

    Args:
        name: Nome do span a ser exibido nos dashboards do CloudWatch.
    """

    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                tracer = get_tracer()
                with tracer.start_as_current_span(name):
                    return await func(*args, **kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                tracer = get_tracer()
                with tracer.start_as_current_span(name):
                    return func(*args, **kwargs)

            return sync_wrapper

    return decorator
