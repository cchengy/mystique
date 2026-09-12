"""Accounts: who is asking, and which key answers for them.

Two things live here, and they are deliberately separate.

**Identity** is Auth0's job. The browser logs in against Auth0 (passkey, via
Universal Login) and sends the resulting access token. We verify it against the
tenant's JWKS - signature, issuer, audience, expiry - and the `sub` claim becomes
the account id. Nothing else identifies a user.

**The model key is NOT Auth0's job.** Token Vault stores OAuth access and refresh
tokens from federated providers over RFC 8693; a key the user brings is not one of
those, and Auth0's own docs say non-OAuth APIs need credential management outside
it. So the key lives here, encrypted at rest, filed under the Auth0 `sub`.

The preferred way to get that key is OpenRouter's own OAuth PKCE flow: the user
authorises on openrouter.ai and we exchange the code for a key scoped to their
account, so they never paste a secret. Pasting stays available for people who
prefer it.

Refusing beats guessing: with no MYSTIQUE_SECRET set, storing a key fails loudly
instead of writing it in the clear.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path
from typing import Any

import httpx2 as httpx
from fastapi import HTTPException

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "").strip().rstrip("/")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "").strip()
SEGREDO = os.getenv("MYSTIQUE_SECRET", "").strip()
CONTAS_DIR = Path(os.getenv("MYSTIQUE_CONTAS_DIR", "workspace/contas"))

OPENROUTER = "https://openrouter.ai/api/v1"


def auth_configurada() -> bool:
    return bool(AUTH0_DOMAIN and AUTH0_AUDIENCE)


# --- cifragem em repouso ------------------------------------------------------
# AES would mean a dependency. This is XChaCha-shaped in spirit only: a keyed
# stream from HMAC-SHA256 plus an authentication tag over the ciphertext. Enough
# that a stolen disk does not hand over the keys, and honest about what it is.

def _fluxo(chave: bytes, nonce: bytes, n: int) -> bytes:
    saida = bytearray()
    contador = 0
    while len(saida) < n:
        saida += hmac.new(chave, nonce + contador.to_bytes(8, "big"), hashlib.sha256).digest()
        contador += 1
    return bytes(saida[:n])


def cifrar(texto: str) -> dict:
    if not SEGREDO:
        raise HTTPException(503, "MYSTIQUE_SECRET is not set: refusing to store a key in the clear.")
    chave = hashlib.sha256(SEGREDO.encode()).digest()
    nonce = secrets.token_bytes(16)
    bruto = texto.encode()
    cifra = bytes(a ^ b for a, b in zip(bruto, _fluxo(chave, nonce, len(bruto))))
    tag = hmac.new(chave, nonce + cifra, hashlib.sha256).hexdigest()
    return {"n": base64.b64encode(nonce).decode(), "c": base64.b64encode(cifra).decode(), "t": tag}


def decifrar(caixa: dict) -> str | None:
    if not SEGREDO or not caixa:
        return None
    try:
        chave = hashlib.sha256(SEGREDO.encode()).digest()
        nonce = base64.b64decode(caixa["n"])
        cifra = base64.b64decode(caixa["c"])
        if not hmac.compare_digest(hmac.new(chave, nonce + cifra, hashlib.sha256).hexdigest(), caixa["t"]):
            return None  # tampered or wrong secret
        return bytes(a ^ b for a, b in zip(cifra, _fluxo(chave, nonce, len(cifra)))).decode()
    except (KeyError, ValueError, TypeError):
        return None


# --- identidade ---------------------------------------------------------------

_JWKS: dict[str, Any] = {"em": 0, "chaves": {}}


async def _jwks() -> dict:
    if _JWKS["chaves"] and time.time() - _JWKS["em"] < 3600:
        return _JWKS["chaves"]
    async with httpx.AsyncClient(timeout=15.0) as http:
        r = await http.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
        r.raise_for_status()
        _JWKS["chaves"] = {k["kid"]: k for k in r.json().get("keys", [])}
        _JWKS["em"] = time.time()
    return _JWKS["chaves"]


def _b64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


async def usuario_do_token(autorizacao: str | None) -> dict | None:
    """Returns the verified claims, or None. Never trusts an unverified token."""
    if not auth_configurada() or not autorizacao or not autorizacao.startswith("Bearer "):
        return None
    token = autorizacao[7:]
    try:
        cabecalho_b64, corpo_b64, assinatura_b64 = token.split(".")
        cabecalho = json.loads(_b64(cabecalho_b64))
        chaves = await _jwks()
        jwk = chaves.get(cabecalho.get("kid"))
        if jwk is None or cabecalho.get("alg") != "RS256":
            return None

        # RS256 check without a crypto dependency: rebuild the modulus and verify
        # PKCS#1 v1.5 by comparing the recovered digest.
        n = int.from_bytes(_b64(jwk["n"]), "big")
        e = int.from_bytes(_b64(jwk["e"]), "big")
        assinatura = int.from_bytes(_b64(assinatura_b64), "big")
        recuperado = pow(assinatura, e, n).to_bytes((n.bit_length() + 7) // 8, "big")
        esperado = hashlib.sha256(f"{cabecalho_b64}.{corpo_b64}".encode()).digest()
        if not recuperado.endswith(esperado) or b"\x00\x01" not in recuperado[:3]:
            return None

        corpo = json.loads(_b64(corpo_b64))
    except Exception:
        return None

    if corpo.get("iss") != f"https://{AUTH0_DOMAIN}/":
        return None
    aud = corpo.get("aud")
    if AUTH0_AUDIENCE not in (aud if isinstance(aud, list) else [aud]):
        return None
    if corpo.get("exp", 0) < time.time():
        return None
    return corpo


# --- a conta ------------------------------------------------------------------

def _arquivo(sub: str) -> Path:
    # The Auth0 sub is not a safe filename (it contains |), so key the file by a
    # digest of it. The sub itself is kept inside, for support.
    return CONTAS_DIR / f"{hashlib.sha256(sub.encode()).hexdigest()[:32]}.json"


def ler_conta(sub: str) -> dict:
    try:
        return json.loads(_arquivo(sub).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"sub": sub}


def gravar_conta(sub: str, dados: dict) -> None:
    CONTAS_DIR.mkdir(parents=True, exist_ok=True)
    destino = _arquivo(sub)
    temporario = destino.with_suffix(".tmp")
    temporario.write_text(json.dumps({**dados, "sub": sub}, ensure_ascii=False, indent=2), encoding="utf-8")
    temporario.replace(destino)
    destino.chmod(0o600)


def guardar_chave(sub: str, chave: str, origem: str) -> dict:
    conta = ler_conta(sub)
    conta["chave"] = cifrar(chave)
    conta["origem"] = origem  # "openrouter-oauth" | "colada"
    conta["em"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    gravar_conta(sub, conta)
    return {"origem": origem, "em": conta["em"]}


def chave_da_conta(sub: str) -> str | None:
    return decifrar(ler_conta(sub).get("chave") or {})


def esquecer_chave(sub: str) -> None:
    conta = ler_conta(sub)
    conta.pop("chave", None)
    conta.pop("origem", None)
    gravar_conta(sub, conta)


def workspace_da_conta(sub: str) -> Path:
    """Her memory is per account: what she learned for one user is not another's."""
    return CONTAS_DIR / hashlib.sha256(sub.encode()).hexdigest()[:32] / "workspace"


# --- OpenRouter ---------------------------------------------------------------

async def trocar_codigo(codigo: str, verificador: str, metodo: str = "S256") -> str:
    """OAuth PKCE: the code becomes a key scoped to the user's own OpenRouter account."""
    async with httpx.AsyncClient(timeout=30.0) as http:
        r = await http.post(
            f"{OPENROUTER}/auth/keys",
            json={"code": codigo, "code_verifier": verificador, "code_challenge_method": metodo},
        )
    if r.status_code >= 400:
        raise HTTPException(400, f"OpenRouter refused the exchange: {r.text[:200]}")
    chave = (r.json() or {}).get("key")
    if not chave:
        raise HTTPException(400, "OpenRouter returned no key.")
    return chave


async def estado_da_chave(chave: str) -> dict:
    """What this key can do, straight from OpenRouter: label, limit, usage, credits."""
    async with httpx.AsyncClient(timeout=20.0) as http:
        cab = {"Authorization": f"Bearer {chave}"}
        chave_info = await http.get(f"{OPENROUTER}/key", headers=cab)
        creditos = await http.get(f"{OPENROUTER}/credits", headers=cab)
    if chave_info.status_code == 401:
        raise HTTPException(401, "OpenRouter rejected this key.")
    return {
        "chave": (chave_info.json() or {}).get("data", {}),
        "creditos": (creditos.json() or {}).get("data", {}) if creditos.status_code < 400 else None,
    }
