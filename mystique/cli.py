"""CLI shared by the good/ and evil/ versions."""

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
        description=f"Mystique ({mundo_cls.modo}): a shapeshifting agent that earns the powers of the agents she meets.",
    )
    parser.add_argument("missao", nargs="?", metavar="mission", help="mission to run; omit for interactive mode")
    parser.add_argument(
        "--budget",
        "--orcamento",
        dest="orcamento",
        metavar="USD",
        type=float,
        default=float(os.getenv("MYSTIQUE_BUDGET_USD", "5")),
        help="Mystique's spending cap in USD per session (default: 5)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="show Mystique's reasoning")
    args = parser.parse_args()

    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")):
        parser.exit(1, "Missing ANTHROPIC_API_KEY. Copy .env.example to .env and fill in the key.\n")

    workspace.mkdir(parents=True, exist_ok=True)
    asyncio.run(executar(args.missao, mundo_cls(workspace), args.orcamento, args.verbose, persona, extras))
