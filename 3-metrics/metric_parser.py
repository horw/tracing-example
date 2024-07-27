import json
import math
import subprocess
import time
import socket
import shutil

import psutil
import re
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.metrics import (
    CallbackOptions,
    Observation,
    get_meter_provider,
    set_meter_provider,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

exporter = OTLPMetricExporter(insecure=True)
reader = PeriodicExportingMetricReader(exporter, math.inf)

provider = MeterProvider(metric_readers=[reader], resource=Resource.create(attributes={
    "service.name": socket.gethostname(),
}))
set_meter_provider(provider)


def get_cpu_usage_callback(_: CallbackOptions):
    for (number, percent) in enumerate(psutil.cpu_percent(percpu=True)):
        attributes = {"cpu_number": str(number)}
        yield Observation(percent, attributes)


def get_folder_memory_usage(_: CallbackOptions):
    command = 'du -c --max-depth=0 /var/log'
    output = subprocess.check_output(command, shell=True)
    for line in output.decode().split('\n'):
        result = re.search("(.+)\ttotal", line)
        if result:
            yield Observation(int(result.group(1)) / 1024 / 1024 / 1024, {"folder-name": 'logs'})


def get_disk_usage(_: CallbackOptions):
    stat = shutil.disk_usage('/')
    yield Observation(stat.used / stat.total)


def get_ram_usage_callback(_: CallbackOptions):
    ram_percent = psutil.virtual_memory().percent
    yield Observation(ram_percent)


def get_docker_usage(_: CallbackOptions):
    command = 'docker system df --format json'
    output = subprocess.check_output(command, shell=True)
    for line in output.decode().split('\n'):
        if not line:
            continue
        data = json.loads(line)
        result = re.search(".+ \((.+)\%\)", data['Reclaimable'])
        if result:
            yield Observation(int(result.group(1)), {"Type": data['Type']})


meter = get_meter_provider().get_meter("getting-started", "0.1.2")

meter.create_observable_gauge(
    callbacks=[get_cpu_usage_callback],
    name="cpu_percent",
    description="per-cpu usage",
    unit="1")

meter.create_observable_gauge(
    callbacks=[get_docker_usage],
    name="docker_reclaimable",
    description="per-type",
    unit="%")

meter.create_observable_gauge(
    callbacks=[get_ram_usage_callback],
    name="ram_usage",
    description="per-type",
    unit="%")

meter.create_observable_gauge(
    callbacks=[get_folder_memory_usage],
    name="folder_size",
    description="per-folder",
    unit="1")

meter.create_observable_gauge(
    callbacks=[get_disk_usage],
    name="disk_usage",
    description="per-folder",
    unit="%")

while True:
    reader.collect()
    time.sleep(10)