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
from pathlib import Path
from typing import Callable

from .contas import workspace_da_conta
from .eventos import BarramentoEventos

_MODOS = {"good": "good", "bem": "good", "evil": "evil", "mal": "evil"}
ANONIMO = "anonimo"


class Mundos:
    """Lazily builds and caches one world per account."""

    def __init__(self, modo: str, raiz: Path) -> None:
        self.modo = _MODOS.get(modo.lower(), "good")
        self.raiz = raiz
        self._por_conta: dict[tuple[str, str], object] = {}
        self._barramentos: dict[str, BarramentoEventos] = {}

    def _workspace(self, sub: str, modo: str) -> Path:
        # The shared account keeps the original on-disk location, so an existing
        # deployment does not lose what it already learned.
        if sub == ANONIMO:
            return self.raiz / modo / "workspace"
        base = workspace_da_conta(sub)
        return base if modo == self.modo else base.parent / f"workspace-{modo}"

    def para(self, sub: str, modo: str | None = None):
        modo = _MODOS.get((modo or self.modo).lower(), self.modo)
        chave = (sub, modo)
        mundo = self._por_conta.get(chave)
        if mundo is not None:
            return mundo

        from .mundo_servidor import MundoBemServidor, MundoMalServidor

        workspace = self._workspace(sub, modo)
        workspace.mkdir(parents=True, exist_ok=True)
        classe = MundoBemServidor if modo == "good" else MundoMalServidor
        # Its own bus as well: events must not cross between accounts.
        # Good and evil sessions remain separate worlds, but the account owns one
        # transport. Switching profile must not silently disconnect the live UI.
        barramento = self._barramentos.setdefault(sub, BarramentoEventos())
        mundo = classe(workspace, eventos=barramento)
        self._por_conta[chave] = mundo
        return mundo

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
