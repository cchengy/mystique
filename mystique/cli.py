"""CLI compartilhada pelas versões bem/ e mal/."""

import argparse
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from .agente import FerramentasExtras, executar
from .mundo import Mundo


def main(mundo_cls: type[Mundo], persona: str, extras: FerramentasExtras, workspace: Path) -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(
        prog=f"python -m {mundo_cls.modo}",
        description=f"Mystique ({mundo_cls.modo}): agente metamorfa que conquista os poderes dos agentes com quem interage.",
    )
    parser.add_argument("missao", nargs="?", help="missão a executar; omita para o modo interativo")
    parser.add_argument(
        "--orcamento",
        type=float,
        default=float(os.getenv("MYSTIQUE_BUDGET_USD", "5")),
        help="teto de gasto da Mystique em USD por sessão (padrão: 5)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="mostra o raciocínio da Mystique")
    args = parser.parse_args()

    workspace.mkdir(parents=True, exist_ok=True)
    asyncio.run(executar(args.missao, mundo_cls(workspace), args.orcamento, args.verbose, persona, extras))
