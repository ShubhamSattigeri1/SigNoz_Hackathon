import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { DocumentLoadInstrumentation } from '@opentelemetry/instrumentation-document-load';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';
import { ZoneContextManager } from '@opentelemetry/context-zone';
import { Resource } from '@opentelemetry/resources';

const SIGNOZ_ENDPOINT = import.meta.env.VITE_SIGNOZ_ENDPOINT || 'https://ingest.us.signoz.cloud:443';
const SIGNOZ_INGESTION_KEY = import.meta.env.VITE_SIGNOZ_INGESTION_KEY || '';

export function initWebTracing() {
  if (!SIGNOZ_INGESTION_KEY) return;
  try {
    const exporter = new OTLPTraceExporter({
      url: `${SIGNOZ_ENDPOINT}/v1/traces`,
      headers: { 'signoz-ingestion-key': SIGNOZ_INGESTION_KEY },
    });

    const provider = new WebTracerProvider({
      resource: new Resource({ 'service.name': 'agent-rca-frontend' }),
    });

    provider.addSpanProcessor(new BatchSpanProcessor(exporter));
    provider.register({ contextManager: new ZoneContextManager() });

    DocumentLoadInstrumentation.create().setTracerProvider(provider);
    FetchInstrumentation.create({
      ignoreUrls: [/signoz\.cloud/],
      propagateTraceHeaderCorsUrls: ['http://localhost:8000/api/*'],
    }).setTracerProvider(provider);
  } catch (e) {
    console.warn('[otel] Failed to init web tracing:', e);
  }
}
