"""Credential broker: the only process allowed to persist provider secrets."""

import base64
import hashlib
import json
import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx2 as httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel

from servidor.contas import usuario_do_token

STORE = Path(os.getenv("MYSTIQUE_VAULT_DIR", "/vault"))
TTL = timedelta(hours=24)
OPENROUTER = "https://openrouter.ai/api/v1"
EXA = "https://api.exa.ai"
MAX_PROXY_BODY = 2 * 1024 * 1024
_OPENROUTER_ROUTES = {
    ("GET", "key"),
    ("GET", "credits"),
    ("POST", "chat/completions"),
}
_EXA_ROUTES = {"search", "contents", "findSimilar"}


async def trocar_codigo(codigo: str, verificador: str, metodo: str = "S256") -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{OPENROUTER}/auth/keys", json={
            "code": codigo, "code_verifier": verificador, "code_challenge_method": metodo,
        })
    if response.status_code >= 400:
        raise HTTPException(400, "OpenRouter refused the OAuth exchange.")
    secret = (response.json() or {}).get("key")
    if not secret:
        raise HTTPException(400, "OpenRouter returned no key.")
    return secret


def _master_key() -> bytes:
    raw = os.getenv("MYSTIQUE_VAULT_KEY", "")
    legacy = os.getenv("MYSTIQUE_LEGACY_SECRET", "")
    if not raw and legacy:
        # One-way, domain-separated migration bridge for existing Dokploy installs.
        # The legacy secret is injected into this container only, never the app.
        return hashlib.sha256(b"mystique-vault-v1\0" + legacy.encode()).digest()
    try:
        key = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))
    except ValueError as error:
        raise RuntimeError("MYSTIQUE_VAULT_KEY must be a base64url key") from error
    if len(key) != 32:
        raise RuntimeError("MYSTIQUE_VAULT_KEY must decode to exactly 32 bytes (or set the broker-only migration secret)")
    return key


def _path(sub: str) -> Path:
    return STORE / f"{hashlib.sha256(sub.encode()).hexdigest()}.json"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _read(sub: str) -> dict:
    try:
        return json.loads(_path(sub).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"providers": {}}


def _write(sub: str, data: dict) -> None:
    STORE.mkdir(parents=True, exist_ok=True)
    target = _path(sub)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    temporary.replace(target)
    target.chmod(0o600)


def _encrypt(sub: str, provider: str, secret: str) -> dict:
    nonce = os.urandom(12)
    aad = f"mystique:v1:{sub}:{provider}".encode()
    ciphertext = AESGCM(_master_key()).encrypt(nonce, secret.encode(), aad)
    return {"v": 1, "n": base64.urlsafe_b64encode(nonce).decode(), "c": base64.urlsafe_b64encode(ciphertext).decode()}


def _decrypt(sub: str, provider: str, box: dict) -> str:
    try:
        aad = f"mystique:v1:{sub}:{provider}".encode()
        return AESGCM(_master_key()).decrypt(base64.urlsafe_b64decode(box["n"]), base64.urlsafe_b64decode(box["c"]), aad).decode()
    except Exception as error:
        raise HTTPException(503, "Stored credential cannot be opened.") from error


def _metadata(record: dict | None) -> dict:
    if not record:
        return {"tem": False}
    expires = datetime.fromisoformat(record["expires_at"])
    if expires <= _now():
        return {"tem": False, "expirada": True, "expira_em": record["expires_at"]}
    return {"tem": True, "origem": record.get("origin"), "criada_em": record["created_at"], "expira_em": record["expires_at"]}


def _credential(sub: str, provider: str) -> str:
    data = _read(sub)
    record = data.get("providers", {}).get(provider)
    meta = _metadata(record)
    if not meta.get("tem"):
        if record:
            data["providers"].pop(provider, None)
            _write(sub, data)
        raise HTTPException(401, f"{provider} credential is missing or expired; reconnect it.")
    return _decrypt(sub, provider, record["box"])


async def _sub(request: Request) -> str:
    claims = await usuario_do_token(request.headers.get("authorization"))
    if claims is None:
        raise HTTPException(401, "A valid Auth0 access token is required.")
    return claims["sub"]


class CredentialBody(BaseModel):
    key: str | None = None
    code: str | None = None
    verifier: str | None = None
    method: str = "S256"


app = FastAPI(title="Mystique credential broker", docs_url=None, redoc_url=None, openapi_url=None)


def purge_expired() -> int:
    removed = 0
    if not STORE.exists():
        return removed
    for path in STORE.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            providers = data.setdefault("providers", {})
            for provider, record in list(providers.items()):
                if not _metadata(record).get("tem"):
                    providers.pop(provider, None)
                    removed += 1
            if providers:
                temporary = path.with_suffix(".tmp")
                temporary.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
                temporary.replace(path)
            else:
                path.unlink(missing_ok=True)
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            continue
    return removed


@asynccontextmanager
async def lifespan(_: FastAPI):
    _master_key()
    async def sweeper() -> None:
        while True:
            purge_expired()
            await asyncio.sleep(3600)
    task = asyncio.create_task(sweeper())
    try:
        yield
    finally:
        task.cancel()


app.router.lifespan_context = lifespan


@app.get("/health")
def health() -> dict:
    _master_key()
    return {"ok": True}


@app.get("/credentials")
async def credentials(request: Request) -> dict:
    sub = await _sub(request)
    data = _read(sub)
    return {provider: _metadata(data.get("providers", {}).get(provider)) for provider in ("openrouter", "exa")}


@app.put("/credentials/{provider}")
async def put_credential(provider: str, body: CredentialBody, request: Request) -> dict:
    if provider not in {"openrouter", "exa"}:
        raise HTTPException(404, "Unknown provider.")
    sub = await _sub(request)
    if provider == "openrouter" and body.code and body.verifier:
        secret, origin = await trocar_codigo(body.code, body.verifier, body.method), "openrouter-oauth"
    elif body.key and body.key.strip():
        secret, origin = body.key.strip(), "pasted"
    else:
        raise HTTPException(400, "Send a provider key or a complete OpenRouter OAuth exchange.")
    headers = {"Authorization": f"Bearer {secret}"} if provider == "openrouter" else {"x-api-key": secret}
    url = f"{OPENROUTER}/key" if provider == "openrouter" else f"{EXA}/search"
    kwargs = {} if provider == "openrouter" else {"json": {"query": "Mystique credential validation", "numResults": 1}}
    async with httpx.AsyncClient(timeout=20.0) as client:
        check = await client.request("GET" if provider == "openrouter" else "POST", url, headers=headers, **kwargs)
    if check.status_code >= 400:
        raise HTTPException(401, f"{provider} rejected this credential.")
    created = _now()
    record = {"origin": origin, "created_at": created.isoformat(), "expires_at": (created + TTL).isoformat(), "box": _encrypt(sub, provider, secret)}
    data = _read(sub)
    data.setdefault("providers", {})[provider] = record
    _write(sub, data)
    return _metadata(record)


@app.delete("/credentials/{provider}", status_code=204)
async def delete_credential(provider: str, request: Request) -> Response:
    sub = await _sub(request)
    data = _read(sub)
    data.setdefault("providers", {}).pop(provider, None)
    _write(sub, data)
    return Response(status_code=204)


@app.delete("/account", status_code=204)
async def delete_account(request: Request) -> Response:
    sub = await _sub(request)
    _path(sub).unlink(missing_ok=True)
    return Response(status_code=204)


@app.api_route("/openrouter/api/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_openrouter(path: str, request: Request) -> Response:
    if (request.method, path) not in _OPENROUTER_ROUTES:
        raise HTTPException(404, "Provider operation is not allowed.")
    sub = await _sub(request)
    secret = _credential(sub, "openrouter")
    body = await request.body()
    if len(body) > MAX_PROXY_BODY:
        raise HTTPException(413, "Provider request is too large.")
    headers = {"Authorization": f"Bearer {secret}", "Content-Type": request.headers.get("content-type", "application/json")}
    async with httpx.AsyncClient(timeout=190.0) as client:
        upstream = await client.request(request.method, f"{OPENROUTER}/{path}", headers=headers, content=body)
    safe_headers = {k: v for k, v in upstream.headers.items() if k.lower() in {"content-type", "retry-after"}}
    return Response(upstream.content, upstream.status_code, safe_headers)


@app.post("/exa/{path:path}")
async def proxy_exa(path: str, request: Request) -> Response:
    if path not in _EXA_ROUTES:
        raise HTTPException(404, "Provider operation is not allowed.")
    sub = await _sub(request)
    secret = _credential(sub, "exa")
    body = await request.body()
    if len(body) > MAX_PROXY_BODY:
        raise HTTPException(413, "Provider request is too large.")
    async with httpx.AsyncClient(timeout=35.0) as client:
        upstream = await client.post(f"{EXA}/{path}", headers={"x-api-key": secret, "Content-Type": "application/json"}, content=body)
    return Response(upstream.content, upstream.status_code, {"Content-Type": upstream.headers.get("content-type", "application/json")})
