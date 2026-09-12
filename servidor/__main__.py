"""Entry point: `python -m servidor`. Reads MYSTIQUE_MODO (good|evil; bem|mal also accepted)
from the environment, boots the matching Mundo, and serves the trust-broker panel."""

import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

# Provider adapters read their defaults while importing. Load the project environment first
# so `python -m servidor` selects the configured OpenAI-compatible backend deterministically.
load_dotenv()

from .app import criar_app
from .eventos import BarramentoEventos
from .mundo_servidor import MundoBemServidor, MundoMalServidor

_MODOS = {"good": "good", "bem": "good", "evil": "evil", "mal": "evil"}


def main() -> None:
    modo = _MODOS.get(os.getenv("MYSTIQUE_MODO", "good").lower(), "good")
    eventos = BarramentoEventos()
    raiz = Path(__file__).resolve().parent.parent

    if modo == "good":
        from good.ferramentas import ferramentas
        from good.persona import PERSONA

        workspace = raiz / "good" / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        mundo = MundoBemServidor(workspace, eventos=eventos)
    else:
        from evil.ferramentas import ferramentas
        from evil.persona import PERSONA

        workspace = raiz / "evil" / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        mundo = MundoMalServidor(workspace, eventos=eventos)

    app = criar_app(mundo, PERSONA, ferramentas)
    porta = int(os.getenv("SERVIDOR_PORTA", "8000"))
    print(f"servidor ({modo}) - http://127.0.0.1:{porta} - stream at /agui/stream")
    uvicorn.run(app, host="127.0.0.1", port=porta)


if __name__ == "__main__":
    main()
