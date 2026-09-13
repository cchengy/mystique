"""Durable, account-scoped conversations for the live UI.

The browser is a view, never the source of truth. Files are deliberately small,
portable JSON documents and writes are atomic so a restart cannot turn an old
chat into a blank model context.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path


def _agora() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


class Sessoes:
    def __init__(self, raiz: Path) -> None:
        self.raiz = raiz

    def _pasta(self, sub: str) -> Path:
        return self.raiz / hashlib.sha256(sub.encode()).hexdigest()[:32] / "sessions"

    def _arquivo(self, sub: str, sessao_id: str) -> Path:
        if not sessao_id or any(c not in "0123456789abcdef" for c in sessao_id):
            raise ValueError("invalid session id")
        return self._pasta(sub) / f"{sessao_id}.json"

    def _gravar(self, sub: str, sessao: dict) -> None:
        pasta = self._pasta(sub)
        pasta.mkdir(parents=True, exist_ok=True)
        destino = self._arquivo(sub, sessao["id"])
        temporario = destino.with_suffix(".tmp")
        temporario.write_text(json.dumps(sessao, ensure_ascii=False, indent=2), encoding="utf-8")
        temporario.replace(destino)
        destino.chmod(0o600)

    def criar(self, sub: str, *, titulo: str = "New conversation", modo: str = "good") -> dict:
        agora = _agora()
        sessao = {
            "id": uuid.uuid4().hex,
            # Stored in the English source language; the UI translates it. A title the
            # user typed is kept verbatim and simply falls through untranslated.
            "titulo": (titulo.strip() or "New conversation")[:80],
            "modo": "evil" if modo == "evil" else "good",
            "mensagens": [],
            "evidencias": [],
            "created_at": agora,
            "updated_at": agora,
        }
        self._gravar(sub, sessao)
        return sessao

    def obter(self, sub: str, sessao_id: str) -> dict | None:
        try:
            return json.loads(self._arquivo(sub, sessao_id).read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            return None

    def listar(self, sub: str) -> list[dict]:
        saida = []
        for arquivo in self._pasta(sub).glob("*.json") if self._pasta(sub).exists() else []:
            try:
                item = json.loads(arquivo.read_text(encoding="utf-8"))
                saida.append({k: item.get(k) for k in ("id", "titulo", "modo", "created_at", "updated_at")})
            except (OSError, json.JSONDecodeError):
                continue
        return sorted(saida, key=lambda x: x.get("updated_at") or "", reverse=True)

    def adicionar(self, sub: str, sessao_id: str, role: str, content: str) -> dict:
        if role not in {"user", "assistant", "system"}:
            raise ValueError("invalid role")
        sessao = self.obter(sub, sessao_id)
        if sessao is None:
            raise KeyError(sessao_id)
        sessao["mensagens"].append({"role": role, "content": content})
        if role == "user" and len([m for m in sessao["mensagens"] if m["role"] == "user"]) == 1:
            sessao["titulo"] = content.strip().replace("\n", " ")[:52] or sessao["titulo"]
        sessao["updated_at"] = _agora()
        self._gravar(sub, sessao)
        return sessao

    def adicionar_evidencia(self, sub: str, sessao_id: str, evidencia: dict) -> None:
        sessao = self.obter(sub, sessao_id)
        if sessao is None:
            raise KeyError(sessao_id)
        if not any(item.get("id") == evidencia.get("id") for item in sessao["evidencias"]):
            sessao["evidencias"].append(evidencia)
            sessao["updated_at"] = _agora()
            self._gravar(sub, sessao)

    def contexto(self, sub: str, sessao_id: str, limite: int = 40) -> list[dict]:
        sessao = self.obter(sub, sessao_id)
        if sessao is None:
            raise KeyError(sessao_id)
        return [m for m in sessao["mensagens"] if m.get("role") in {"user", "assistant"}][-limite:]
