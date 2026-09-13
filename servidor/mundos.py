"""One world per account.

Until now the server held a single Mundo and a single event bus shared by every
browser, so two people connected at once watched the same conversation and wrote
into the same memory. With accounts that stops being a missing feature and starts
being a privacy problem, so worlds are now keyed by the Auth0 `sub`.

Each account gets its own workspace, which is what makes her memory per account:
the reasoning bank, the adapters and the audits she writes for one user are not
another user's.

With no tenant configured every caller resolves to the same "anonimo" world, which
is exactly the single-world behaviour local development had before.
"""

import os
import asyncio
from pathlib import Path
from typing import Callable

from .contas import workspace_da_conta
from .eventos import BarramentoEventos

_MODOS = {"good": "good", "bem": "good", "evil": "evil", "mal": "evil"}
ANONIMO = "anonimo"


# One live world per open conversation, capped so a long day of chatting does not
# hold every world an account ever opened.
MAX_MUNDOS_POR_CONTA = 8


class Mundos:
    """One world per conversation, not per account.

    A world carries the run in progress and the event stream the browser is
    watching. Keyed by account alone, two conversations shared both: starting a
    run in one and switching to the other in the UI showed its output there.
    The workspace is still per account and profile - the Reasoning Bank and the
    adapters are her memory, and that memory is the account's, not one chat's.
    """

    def __init__(self, modo: str, raiz: Path) -> None:
        self.modo = _MODOS.get(modo.lower(), "good")
        self.raiz = raiz
        self._por_conta: dict[tuple[str, str, str], object] = {}
        self._barramentos: dict[tuple[str, str], BarramentoEventos] = {}

    def _workspace(self, sub: str, modo: str) -> Path:
        # The shared account keeps the original on-disk location, so an existing
        # deployment does not lose what it already learned.
        if sub == ANONIMO:
            return self.raiz / modo / "workspace"
        base = workspace_da_conta(sub)
        return base if modo == self.modo else base.parent / f"workspace-{modo}"

    def para(self, sub: str, modo: str | None = None, sessao: str = ""):
        modo = _MODOS.get((modo or self.modo).lower(), self.modo)
        chave = (sub, modo, sessao)
        mundo = self._por_conta.get(chave)
        if mundo is not None:
            self._por_conta[chave] = self._por_conta.pop(chave)   # most recently used
            return mundo

        from .mundo_servidor import MundoBemServidor, MundoMalServidor

        workspace = self._workspace(sub, modo)
        workspace.mkdir(parents=True, exist_ok=True)
        classe = MundoBemServidor if modo == "good" else MundoMalServidor
        # One bus per conversation: an event belongs to the chat that produced it.
        barramento = self._barramentos.setdefault((sub, sessao), BarramentoEventos())
        mundo = classe(workspace, eventos=barramento)
        self._por_conta[chave] = mundo
        self._podar(sub)
        return mundo

    def _podar(self, sub: str) -> None:
        """Forget the least recently used worlds of an account, never a running one."""
        chaves = [chave for chave in self._por_conta if chave[0] == sub]
        for chave in chaves[:-MAX_MUNDOS_POR_CONTA]:
            mundo = self._por_conta.get(chave)
            if getattr(mundo, "ocupado", False):
                continue
            self._por_conta.pop(chave, None)
            if not any(c[0] == chave[0] and c[2] == chave[2] for c in self._por_conta):
                self._barramentos.pop((chave[0], chave[2]), None)

    def existentes(self, sub: str) -> list:
        """Worlds already live for this account, in no particular order.

        Used to resolve something whose mode the request does not carry, without
        building - and writing a workspace for - a mode the account never opened.
        """
        return [mundo for chave, mundo in self._por_conta.items() if chave[0] == sub]

    async def apagar(self, sub: str) -> None:
        """Evict live state and close provider clients before deleting an account."""
        for chave in [chave for chave in self._por_conta if chave[0] == sub]:
            mundo = self._por_conta.pop(chave)
            cliente = getattr(mundo, "_cliente", None)
            fechar = getattr(getattr(cliente, "_http", None), "aclose", None)
            if fechar:
                await fechar()
        for chave in [chave for chave in self._barramentos if chave[0] == sub]:
            self._barramentos.pop(chave, None)

    def contexto(self, modo: str | None = None) -> tuple[str, Callable]:
        """(persona, extras) for the configured mode."""
        if (modo or self.modo) == "good":
            from good.ferramentas import ferramentas
            from good.persona import PERSONA
        else:
            from evil.ferramentas import ferramentas
            from evil.persona import PERSONA
        return PERSONA, ferramentas


def modo_configurado() -> str:
    return _MODOS.get(os.getenv("MYSTIQUE_MODO", "good").lower(), "good")
