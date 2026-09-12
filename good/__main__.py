from pathlib import Path

from mystique.cli import main

from .ferramentas import ferramentas
from .mundo import MundoBem
from .persona import PERSONA

main(MundoBem, PERSONA, ferramentas, workspace=Path(__file__).resolve().parent / "workspace")
