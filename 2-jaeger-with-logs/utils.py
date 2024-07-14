import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk._logs._internal.export import ConsoleLogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
import os


def setup_logging_otlp(logger_name, app_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.NOTSET)
    logger_provider = LoggerProvider(
        resource=Resource.create(
            {
                "service.name": app_name,
                "service.instance.id": os.uname().nodename,
            }
        ),
    )
    set_logger_provider(logger_provider)
    # console_exporter = ConsoleLogExporter()
    # logger_provider.add_log_record_processor(BatchLogRecordProcessor(console_exporter))
    otlp_log_exporter = OTLPLogExporter(endpoint="http://localhost:4317")
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    logger.addHandler(handler)


def setup_otlp(app, app_name, endpoint="http://localhost:4317/"):
    resource = Resource.create(attributes={
        "service.name": app_name,
        "compose_service": app_name
    })

    tracer = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer)

    tracer.add_span_processor(BatchSpanProcessor(
        OTLPSpanExporter(endpoint=endpoint)))

    setup_logging_otlp("otlp", app_name)
    HTTPXClientInstrumentor().instrument()

    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)
