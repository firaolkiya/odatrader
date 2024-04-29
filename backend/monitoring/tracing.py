"""OpenTelemetry tracing stub for gateway→engine→exec→api flow."""
import logging
import time
import uuid
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger("odatrade.tracing")

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


class TracingService:
    def __init__(self, service_name: str = "odatrade"):
        self.service_name = service_name
        self._spans: list = []
        if OTEL_AVAILABLE:
            trace.set_tracer_provider(TracerProvider())
            self.tracer = trace.get_tracer(service_name)
        else:
            self.tracer = None

    @contextmanager
    def span(self, name: str, attributes: dict = None):
        span_id = str(uuid.uuid4())[:8]
        start = time.time()
        entry = {"name": name, "span_id": span_id, "start": start, "attributes": attributes or {}}
        try:
            if self.tracer:
                with self.tracer.start_as_current_span(name) as otel_span:
                    if attributes:
                        for k, v in attributes.items():
                            otel_span.set_attribute(k, str(v))
                    yield span_id
            else:
                yield span_id
        finally:
            entry["duration_ms"] = (time.time() - start) * 1000
            self._spans.append(entry)
            if len(self._spans) > 1000:
                self._spans.pop(0)

    def recent_spans(self, limit: int = 50) -> list:
        return self._spans[-limit:]


tracing = TracingService()
