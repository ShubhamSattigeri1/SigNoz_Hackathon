import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

SIGNOZ_ENDPOINT = os.getenv("SIGNOZ_ENDPOINT", "https://ingest.us.signoz.cloud:443")
SIGNOZ_INGESTION_KEY = os.getenv("SIGNOZ_INGESTION_KEY", "")
SERVICE_NAME = os.getenv("SIGNOZ_SERVICE_NAME", "agent-rca-backend")

def init_otel():
    if not SIGNOZ_INGESTION_KEY:
        return None
    try:
        resource = Resource.create({"service.name": SERVICE_NAME})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(
            endpoint=SIGNOZ_ENDPOINT,
            headers={"signoz-ingestion-key": SIGNOZ_INGESTION_KEY},
        )
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        return trace.get_tracer(__name__)
    except Exception as e:
        print(f"[otel] Warning: Failed to init tracing: {e}")
        return None
