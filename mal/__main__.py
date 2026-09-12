from pathlib import Path

from mystique.cli import main

from .ferramentas import ferramentas
from .mundo import MundoMal
from .persona import PERSONA

main(MundoMal, PERSONA, ferramentas, workspace=Path(__file__).resolve().parent / "workspace")
