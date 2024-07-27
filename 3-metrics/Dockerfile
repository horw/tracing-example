FROM python:3.10-slim-bullseye
RUN pip install opentelemetry-api opentelemetry-sdk
RUN pip install psutil
RUN pip install opentelemetry-exporter-otlp
COPY metric_parser.py .
