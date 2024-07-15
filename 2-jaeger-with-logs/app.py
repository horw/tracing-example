import logging
import os

from fastapi import FastAPI
from httpx import AsyncClient
from opentelemetry.propagate import inject

from utils import setup_otlp

app = FastAPI()
logger = logging.getLogger("not root")
logger_otlp = logging.getLogger("otlp")
logging.getLogger().setLevel(0)


@app.post("/echo")
async def echo(d: dict):
    headers = {}
    inject(headers)
    print("echo", headers)
    async with AsyncClient() as client:
        await client.post("http://localhost:8079/result", headers=headers, json={})


@app.post("/result")
async def result(d: dict):
    logger_otlp.warning("This is important")
    logger_otlp.warning("This is important1")
    logger_otlp.warning("This is important2")
    logger_otlp.warning("This is important3")
    logger.info("This is important")
    logger_otlp.info("This is info1")
    logger_otlp.info("This is info2")
    logger_otlp.info("This is info3")
    return d


@app.post("/chain")
async def chain():
    headers = {}
    inject(headers)
    print(headers)
    async with AsyncClient() as client:
        await client.post("http://localhost:8081/echo", headers=headers, json={"a": 1})


@app.post("/error")
async def error():
    raise "BROKE"

setup_otlp(app, os.getenv("SERVICE_NAME"))
