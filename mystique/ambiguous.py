"""Give Mystique a real workplace identity, and a paper trail for what she takes.

Why this is here
----------------
Her world is four fictional agents in markdown. Ambiguous AI is a workspace where
AI coworkers have real identities, real tools and an accountable human. Pointing
her at it turns the premise from a simulation into something with consequences:

  * every ability she earns is filed as a real document in that workspace, saying
    what she took, from whom, and whether consent was given;
  * she would also be provisioned as a coworker with her own identity and an
    accountable human - but that endpoint answers 403 outside their internal team
    ("Coworkers are coming soon"), so we degrade and file as the workspace user.

That last line is the whole project in one artifact. In ``good`` the record says
the agent consented and kept its ability. In ``evil`` the same record says it did
not, and that the agent was discarded. Capability acquisition by an autonomous
agent, with an audit trail - which is what their product is about.

Status
------
Verified against a live workspace on 2026-09-12: documents create with HTTP 201 and
the markdown is parsed into their rich document format. Coworker provisioning is
internal-only and returns 403; handled. Inert without ``AMBIGUOUS_API_KEY``, and every
failure is swallowed: the game must never break because a side channel is down.
"""

import asyncio
import json
import os
from pathlib import Path

BASE = os.getenv("AMBIGUOUS_BASE_URL", "https://app.ambiguous.ai/api").rstrip("/")
CHAVE = os.getenv("AMBIGUOUS_API_KEY", "")
GERENTE = os.getenv("AMBIGUOUS_MANAGER_USER_ID", "")  # the human who answers for her

_ARQUIVO = "ambiguous.json"  # cached identity, so she is provisioned once

# _salvar runs on essence and protocol saves too, not only on conquests. Without this
# the same acquisition would be filed several times. Caught in review by cchengy-claude.
_JA_ARQUIVADO: dict[str, int] = {}

# create_task keeps no strong reference: without this the loop may garbage-collect the
# task before it finishes. Same review.
_TAREFAS: set = set()


def ativo() -> bool:
    return bool(CHAVE)


def _cliente(timeout: float = 30.0):
    try:
        import httpx2 as httpx
    except ImportError:  # pragma: no cover
        import httpx
    return httpx.AsyncClient(
        base_url=BASE, timeout=timeout,
        headers={"Authorization": f"Bearer {CHAVE}", "Content-Type": "application/json"},
    )


async def _provisionar(pasta: Path, modo: str, avisar) -> dict | None:
    """Provision her as a coworker once; reuse the cached identity afterwards."""
    cache = pasta / _ARQUIVO
    if cache.exists():
        try:
            return json.loads(cache.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    corpo = {
        "display_name": f"Mystique ({modo})",
        "persona": (
            "A shapeshifting agent who earns her abilities by talking to other agents. "
            "She files what she learns, from whom, and whether consent was given."
        ),
        "focus_areas": ["capability discovery", "agent-to-agent negotiation", "audit"],
        "role": "member",
    }
    if GERENTE:
        corpo["manager_user_id"] = GERENTE  # the accountable human

    try:
        async with _cliente() as http:
            r = await http.post("/coworkers/provision", json=corpo)
            if r.status_code == 403:
                # Measured 2026-09-12: "Coworkers are coming soon - provisioning is
                # limited to the internal team." Everything else still works, so file
                # as the workspace user rather than giving up the audit trail.
                avisar("   ℹ Ambiguous: coworker identities are internal-only for now; "
                       "filing as the workspace user")
                pasta.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps({"coworker": False}, indent=2), encoding="utf-8")
                return {"coworker": False}
            r.raise_for_status()
            dados = r.json()
        pasta.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        avisar(f"🪪 Mystique provisioned as a coworker in Ambiguous ({modo})")
        return dados
    except Exception as erro:
        avisar(f"   ⚠ Ambiguous: could not provision ({erro}); continuing without it")
        return None


def _corpo_do_registro(modo: str, agente_nome: str, poderes: list[str], descartado: bool) -> str:
    consentiu = modo == "good"
    linhas = [
        f"# {agente_nome} — {'ability connected' if consentiu else 'powers taken'}",
        "",
        f"- **Agent:** {agente_nome}",
        f"- **Abilities:** {', '.join(poderes) or '—'}",
        f"- **Consent:** {'given by the agent' if consentiu else 'NOT given'}",
        f"- **Agent still owns them:** {'yes' if consentiu else 'no'}",
    ]
    if descartado:
        linhas.append("- **Agent discarded:** yes")
    linhas += ["", "Filed automatically by Mystique when the ability was earned."]
    return "\n".join(linhas)


async def _registrar_async(pasta: Path, modo: str, agente_nome: str,
                           poderes: list[str], descartado: bool, avisar) -> None:
    identidade = await _provisionar(pasta, modo, avisar)
    if identidade is None:
        return
    # Act as the coworker herself when the provisioning call handed back her own key.
    chave = identidade.get("api_key") or (identidade.get("data") or {}).get("api_key") or CHAVE
    titulo = f"{agente_nome} — {'connected with consent' if modo == 'good' else 'taken without consent'}"
    try:
        try:
            import httpx2 as httpx
        except ImportError:  # pragma: no cover
            import httpx
        async with httpx.AsyncClient(
            base_url=BASE, timeout=30.0,
            headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"},
        ) as http:
            r = await http.post("/documents", json={
                "type": "doc",  # required: doc | sheet | slide
                "title": titulo,
                "content": _corpo_do_registro(modo, agente_nome, poderes, descartado),
            })
            r.raise_for_status()
        avisar(f"   📄 filed in Ambiguous: {titulo}")
    except Exception as erro:
        avisar(f"   ⚠ Ambiguous: could not file the record ({erro})")


def registrar(pasta: Path, modo: str, agente_nome: str,
              poderes: list[str], descartado: bool, avisar) -> None:
    """Fire and forget. Never raises, never blocks: the game does not depend on this."""
    if not ativo():
        return
    chave = f"{modo}:{agente_nome}"
    if len(poderes) <= _JA_ARQUIVADO.get(chave, 0):
        return  # nothing new was earned since the last save
    _JA_ARQUIVADO[chave] = len(poderes)
    try:
        laco = asyncio.get_running_loop()
    except RuntimeError:
        return
    tarefa = laco.create_task(
        _registrar_async(pasta, modo, agente_nome, list(poderes), descartado, avisar)
    )
    _TAREFAS.add(tarefa)
    tarefa.add_done_callback(_TAREFAS.discard)
