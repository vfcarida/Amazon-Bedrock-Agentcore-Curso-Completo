"""Módulo de observabilidade e telemetria OpenTelemetry para o AgentCore."""

from .tracer import get_tracer, setup_telemetry, trace_span

__all__ = ["setup_telemetry", "get_tracer", "trace_span"]
