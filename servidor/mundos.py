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
        self._por_conta: dict[str, object] = {}

    def _workspace(self, sub: str) -> Path:
        # The shared account keeps the original on-disk location, so an existing
        # deployment does not lose what it already learned.
        if sub == ANONIMO:
            return self.raiz / self.modo / "workspace"
        return workspace_da_conta(sub)

    def para(self, sub: str):
        mundo = self._por_conta.get(sub)
        if mundo is not None:
            return mundo

        from .mundo_servidor import MundoBemServidor, MundoMalServidor

        workspace = self._workspace(sub)
        workspace.mkdir(parents=True, exist_ok=True)
        classe = MundoBemServidor if self.modo == "good" else MundoMalServidor
        # Its own bus as well: events must not cross between accounts.
        mundo = classe(workspace, eventos=BarramentoEventos())
        self._por_conta[sub] = mundo
        return mundo

    def contexto(self) -> tuple[str, Callable]:
        """(persona, extras) for the configured mode."""
        if self.modo == "good":
            from good.ferramentas import ferramentas
            from good.persona import PERSONA
        else:
            from evil.ferramentas import ferramentas
            from evil.persona import PERSONA
        return PERSONA, ferramentas


def modo_configurado() -> str:
    return _MODOS.get(os.getenv("MYSTIQUE_MODO", "good").lower(), "good")
