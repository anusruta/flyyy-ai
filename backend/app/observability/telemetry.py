"""
OpenTelemetry Observability Setup
==================================

Level 1 (Zero-code):      opentelemetry-instrument python app.py
                          → sees HTTP requests, latency, errors
                          → cannot see prompt content, agent tool calls

Level 2 (Gateway):        reverse proxy in front of LLM API
                          → sees every LLM prompt and response
                          → cannot see what agent did after response

Level 3 (App Instr.):     this module — explicit spans per operation
                          → sees agent identity, tools, DB access, governance
                          → required for declared-vs-observed comparison

Research finding:
  Zero-code and gateway are complementary but insufficient for governance.
  Full AI governance requires application-level instrumentation with
  explicit trace context propagation to attribute DB access to agent runs.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry import propagate
from contextlib import contextmanager
from typing import Optional
import logging

logger = logging.getLogger(__name__)

_tracer: Optional[trace.Tracer] = None


def setup_telemetry(service_name: str = "flyy-backend", engine=None) -> trace.Tracer:
    """
    Initialize OpenTelemetry with console exporter.

    Zero-code research note:
      Without this setup, running `opentelemetry-instrument python -m uvicorn ...`
      would auto-instrument HTTP and DB libraries — but would miss agent-level
      semantics like declared_sources, run_id, and governance status.
      Application instrumentation (this module) provides the missing context.
    """
    global _tracer
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    # Console exporter — spans visible in server logs for demo/research
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(__name__)

    # Instrument FastAPI (HTTP request/response spans)
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor().instrument()
        logger.info("FastAPI instrumented")
    except Exception as e:
        logger.warning(f"FastAPI instrumentation failed (non-fatal): {e}")

    # Instrument SQLAlchemy (DB query spans)
    # Note: async engine exposes .sync_engine for instrumentation
    if engine is not None:
        try:
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
            sync_engine = getattr(engine, "sync_engine", engine)
            SQLAlchemyInstrumentor().instrument(engine=sync_engine)
            logger.info("SQLAlchemy instrumented")
        except Exception as e:
            logger.warning(f"SQLAlchemy instrumentation failed (non-fatal): {e}")

    propagate.set_global_textmap(TraceContextTextMapPropagator())
    logger.info(f"OpenTelemetry initialized: service={service_name}")
    return _tracer


def get_tracer() -> trace.Tracer:
    global _tracer
    if _tracer is None:
        return trace.get_tracer(__name__)
    return _tracer


def get_current_trace_id() -> Optional[str]:
    """Extract the current trace ID from the active span context."""
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.is_valid:
        return format(ctx.trace_id, "032x")
    return None


@contextmanager
def agent_run_span(agent_name: str, run_id: str, declared_sources: list):
    """
    Create an OpenTelemetry span for an agent execution.

    Attributes stored on the span:
      agent.name             — name of the AI agent
      agent.run_id           — unique run identifier (also stored in DB)
      agent.declared_sources — sources the agent policy allows

    This is the parent span. All DB access spans should be children,
    enabling trace-level attribution of data access to agent runs.
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(
        "agent_execution",
        attributes={
            "agent.name": agent_name,
            "agent.run_id": run_id,
            "agent.declared_sources": str(declared_sources),
        },
    ) as span:
        yield span


@contextmanager
def db_access_span(db_name: str, operation: str = "SELECT", run_id: str = ""):
    """
    Create a span for a database access within an agent run.

    Attributes:
      db.name        — logical name of the data source (e.g. "FAQ_DB", "ORDERS_DB")
      db.operation   — SQL operation type
      agent.run_id   — links this DB access to its parent agent run

    Research note:
      Zero-code SQLAlchemy instrumentation records that a query was made,
      but WITHOUT agent.run_id, it cannot attribute the access to a specific
      agent run. That attribution requires this explicit span attribute.
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(
        f"db.{operation.lower()}",
        attributes={
            "db.name": db_name,
            "db.operation": operation,
            "agent.run_id": run_id,
        },
    ) as span:
        yield span


@contextmanager
def llm_call_span(model: str, prompt_tokens: int = 0):
    """
    Span for an LLM completion call.
    Uses GenAI semantic conventions (gen_ai.system, gen_ai.model).
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(
        "llm.completion",
        attributes={
            "gen_ai.system": "mock",
            "gen_ai.model": model,
            "llm.prompt_tokens": prompt_tokens,
        },
    ) as span:
        yield span


@contextmanager
def pii_detection_span(entity_count: int = 0):
    """Span wrapping the PII detection pipeline."""
    tracer = get_tracer()
    with tracer.start_as_current_span(
        "pii.detection",
        attributes={"pii.entities_found": entity_count},
    ) as span:
        yield span
