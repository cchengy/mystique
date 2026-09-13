"""Accounts: who is asking, and which key answers for them.

Two things live here, and they are deliberately separate.

**Identity** is Auth0's job. The browser logs in against Auth0 (passkey, via
Universal Login) and sends the resulting access token. We verify it against the
tenant's JWKS - signature, issuer, audience, expiry - and the `sub` claim becomes
the account id. Nothing else identifies a user.

Provider credentials deliberately do not live here. The isolated ``cofre`` service
owns their encryption, persistence, expiry and provider proxying.
"""

import base64
import hashlib
import json
import os
import shutil
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx2 as httpx
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "").strip().rstrip("/")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "").strip()
CONTAS_DIR = Path(os.getenv("MYSTIQUE_CONTAS_DIR", "workspace/contas"))

OPENROUTER = "https://openrouter.ai/api/v1"
MODELO_PADRAO = os.getenv("MYSTIQUE_OPENROUTER_MODEL", "openrouter/auto").strip()


def auth_configurada() -> bool:
    return bool(AUTH0_DOMAIN and AUTH0_AUDIENCE)


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

        n = int.from_bytes(_b64(jwk["n"]), "big")
        e = int.from_bytes(_b64(jwk["e"]), "big")
        public_key = rsa.RSAPublicNumbers(e, n).public_key()
        public_key.verify(
            _b64(assinatura_b64), f"{cabecalho_b64}.{corpo_b64}".encode(),
            padding.PKCS1v15(), hashes.SHA256(),
        )

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


def modelo_da_conta(sub: str) -> str:
    return ler_conta(sub).get("modelo") or MODELO_PADRAO


def guardar_modelo(sub: str, modelo: str) -> None:
    conta = ler_conta(sub)
    conta["modelo"] = modelo
    gravar_conta(sub, conta)


ONBOARDING = "v1"


def onboarding_visto(sub: str) -> bool:
    """Whether this account has already been walked through the interface.

    Kept on the account, not in the browser: the tour belongs to the person, so
    it does not reappear on a second device and is not lost by clearing a cache.
    """
    return ler_conta(sub).get("onboarding") == ONBOARDING


def marcar_onboarding(sub: str, visto: bool = True) -> bool:
    conta = ler_conta(sub)
    conta["onboarding"] = ONBOARDING if visto else None
    gravar_conta(sub, conta)
    return visto


def workspace_da_conta(sub: str) -> Path:
    """Her memory is per account: what she learned for one user is not another's."""
    return CONTAS_DIR / hashlib.sha256(sub.encode()).hexdigest()[:32] / "workspace"


_RETENCAO = timedelta(days=60)


def registrar_acesso(sub: str, agora: datetime | None = None) -> dict:
    """Record only lifecycle metadata; private data must move to opaque envelopes."""
    instante = (agora or datetime.now(timezone.utc)).astimezone(timezone.utc)
    conta = ler_conta(sub)
    anterior = conta.get("last_access_at")
    if anterior:
        try:
            instante = max(instante, datetime.fromisoformat(anterior))
        except ValueError:
            pass
    conta["last_access_at"] = instante.isoformat()
    conta["delete_after"] = (instante + _RETENCAO).isoformat()
    gravar_conta(sub, conta)
    return {"last_access_at": conta["last_access_at"], "delete_after": conta["delete_after"]}


def apagar_conta(sub: str) -> None:
    """Idempotently remove every application-owned artifact for one account."""
    arquivo = _arquivo(sub)
    try:
        arquivo.unlink()
    except FileNotFoundError:
        pass
    shutil.rmtree(workspace_da_conta(sub).parent, ignore_errors=True)


def expirar_contas_inativas(agora: str | datetime | None = None) -> int:
    """Delete accounts whose explicit 60-day deadline has passed."""
    instante = datetime.fromisoformat(agora) if isinstance(agora, str) else (agora or datetime.now(timezone.utc))
    if instante.tzinfo is None:
        instante = instante.replace(tzinfo=timezone.utc)
    removidas = 0
    if not CONTAS_DIR.exists():
        return removidas
    for arquivo in list(CONTAS_DIR.glob("*.json")):
        try:
            conta = json.loads(arquivo.read_text(encoding="utf-8"))
            prazo = datetime.fromisoformat(conta.get("delete_after") or conta["last_access_at"])
            if "delete_after" not in conta:
                prazo += _RETENCAO
            if prazo > instante:
                continue
            apagar_conta(conta["sub"])
            removidas += 1
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            continue
    return removidas


def contas_vencidas(agora: datetime | None = None) -> list[str]:
    """Return account subjects past their deadline without mutating storage."""
    instante = agora or datetime.now(timezone.utc)
    vencidas: list[str] = []
    if not CONTAS_DIR.exists():
        return vencidas
    for arquivo in CONTAS_DIR.glob("*.json"):
        try:
            conta = json.loads(arquivo.read_text(encoding="utf-8"))
            prazo = datetime.fromisoformat(conta.get("delete_after") or conta["last_access_at"])
            if "delete_after" not in conta:
                prazo += _RETENCAO
            if prazo <= instante:
                vencidas.append(conta["sub"])
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            continue
    return vencidas
