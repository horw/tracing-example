import os

from fastapi import FastAPI
from httpx import AsyncClient
from opentelemetry.propagate import inject

from utils import setup_otlp

app = FastAPI()


@app.post("/echo")
async def echo(d: dict):
    return d


@app.post("/chain")
async def chain():
    headers = {}
    inject(headers)
    async with AsyncClient() as client:
        await client.post("http://localhost:8081/echo", headers=headers)


setup_otlp(app, os.getenv("SERVICE_NAME"))
