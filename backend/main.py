import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="API",
    version="0.1.0",
)

CRUSTDATA_API_KEY = os.environ.get("CRUSTDATA_API_KEY", "")
CRUSTDATA_BASE_URL = "https://api.crustdata.com"


class Condition(BaseModel):
    field: str
    type: str
    value: Any


class Filters(BaseModel):
    op: str
    conditions: list[Condition]


class PersonSearchRequest(BaseModel):
    filters: Filters
    limit: int = 10


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/person/search")
async def person_search(request: PersonSearchRequest):
    if not CRUSTDATA_API_KEY:
        raise HTTPException(status_code=500, detail="CRUSTDATA_API_KEY not configured")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CRUSTDATA_BASE_URL}/person/search",
            headers={
                "Authorization": f"Bearer {CRUSTDATA_API_KEY}",
                "Content-Type": "application/json",
                "x-api-version": "2025-11-01",
            },
            json=request.model_dump(),
            timeout=30.0,
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()
