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
from .mundos import Mundos, modo_configurado


def main() -> None:
    modo = modo_configurado()
    raiz = Path(__file__).resolve().parent.parent
    # One world per account, built on demand. With no tenant configured every
    # caller shares the "anonimo" world, which is the old single-world behaviour.
    mundos = Mundos(modo, raiz)
    persona, ferramentas = mundos.contexto()
    app = criar_app(mundos, persona, ferramentas)
    porta = int(os.getenv("SERVIDOR_PORTA", "8000"))
    host = os.getenv("SERVIDOR_HOST", "127.0.0.1")
    print(f"servidor ({modo}) - http://{host}:{porta} - stream at /agui/stream")
    uvicorn.run(app, host=host, port=porta)


if __name__ == "__main__":
    main()
