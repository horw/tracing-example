from opentelemetry.propagate import extract


from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
resource = Resource.create(attributes={
    "service.name": "ping",
    "compose_service": "ping"
})

tracer = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer)

tracer.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://localhost:4317")))


header = {'traceparent': '00-df04b9b6470019fb6b40e866ad13029d-c31354ae85a52143-01'}
context = extract(header)


with tracer.get_tracer(__name__).start_as_current_span("roll", context=context) as span:
    print('lalla')