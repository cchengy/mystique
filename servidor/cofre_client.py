"""Narrow client for the isolated credential broker.

The application never mounts the broker store or its encryption key.  A verified
Auth0 access token is forwarded as the per-user capability for provider calls.
"""

import os

import httpx2 as httpx
from fastapi import HTTPException

COFRE_URL = os.getenv("MYSTIQUE_CREDENTIAL_BROKER_URL", "http://credential-broker:8001").rstrip("/")


async def pedir(method: str, path: str, authorization: str | None, json: dict | None = None) -> dict:
    headers = {"Authorization": authorization} if authorization else {}
    try:
        async with httpx.AsyncClient(timeout=35.0) as client:
            response = await client.request(method, f"{COFRE_URL}{path}", headers=headers, json=json)
    except httpx.HTTPError as error:
        raise HTTPException(503, "The credential broker is unavailable.") from error
    if response.status_code >= 400:
        detail = "Credential broker refused the request."
        try:
            detail = response.json().get("detail") or detail
        except ValueError:
            pass
        raise HTTPException(response.status_code, detail)
    return response.json() if response.content else {}
