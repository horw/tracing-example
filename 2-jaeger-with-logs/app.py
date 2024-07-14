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
    logger_otlp.warning("This is important")
    logger.info("This is important")
    logger_otlp.info("This is info")
    return d


@app.post("/chain")
async def chain():
    headers = {}
    inject(headers)
    async with AsyncClient() as client:
        await client.post("http://localhost:8081/echo", headers=headers)


@app.post("/error")
async def error():
    raise "BROKE"

setup_otlp(app, os.getenv("SERVICE_NAME"))
