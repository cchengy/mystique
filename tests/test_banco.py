"""The ReasoningBank must reach Mystique, and never the judge.

The bank exists so a failed identification is not thrown away: the next attempt
on the same agent starts from what already did not work. That only happens if
the recall is returned to *her*. Feeding it to the judge instead does the
opposite of the intent - it biases an evaluator that already knows the answer -
and leaves her repeating herself.
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from good.mundo import MundoBem  # noqa: E402
from mystique.mundo import Agente  # noqa: E402
from mystique.poderes import PODERES  # noqa: E402


def _mundo(pasta: Path) -> MundoBem:
    mundo = MundoBem(pasta)
    mundo.avisar = lambda *a, **k: None
    return mundo


def _agente(poder: str) -> Agente:
    agente = Agente(id="byte", nome="Byte", apresentacao="oi", segredo="x", poderes=[poder])
    agente.observados.add(poder)
    return agente


def test_recall_reaches_mystique_and_not_the_judge() -> None:
    poder = sorted(PODERES)[0]
    with tempfile.TemporaryDirectory() as folder:
        mundo = _mundo(Path(folder))
        agente = _agente(poder)
        absorcao = mundo._absorcao(agente)
        vistos: list[str] = []

        async def julgar_recusando(candidatos, descricao, evidencia):
            vistos.append(evidencia)
            return None, "no"

        mundo._julgar = julgar_recusando
        asyncio.run(mundo._identificar(agente, absorcao, "it counts stars", "she saw it"))
        segundo = asyncio.run(mundo._identificar(agente, absorcao, "it counts moons", "she saw it again"))

        # Her own earlier description comes back to her, with the failure marked.
        assert "it counts stars" in segundo[1]
        assert "did not work" in segundo[1]
        # ...and never to the judge, in either call.
        assert all("it counts stars" not in evidencia for evidencia in vistos)
        # The judge's words stay out of what she reads.
        assert "no" not in segundo[1].split("judge")[0].replace("not", "")


def test_usage_count_only_grows_when_the_trace_is_actually_reused() -> None:
    poder = sorted(PODERES)[0]
    with tempfile.TemporaryDirectory() as folder:
        mundo = _mundo(Path(folder))
        agente = _agente(poder)
        absorcao = mundo._absorcao(agente)

        async def julgar_recusando(candidatos, descricao, evidencia):
            return None, "no"

        mundo._julgar = julgar_recusando
        asyncio.run(mundo._identificar(agente, absorcao, "first guess", "evidence"))
        traco = mundo.banco.todos()[0]
        assert traco["usage_count"] == 0, "a trace nobody read back must not count as reused"

        asyncio.run(mundo._identificar(agente, absorcao, "second guess", "evidence"))
        primeiro = [t for t in mundo.banco.todos() if t["description"] == "first guess"][0]
        assert primeiro["usage_count"] == 1


def test_the_wiki_is_written_next_to_the_bank() -> None:
    with tempfile.TemporaryDirectory() as folder:
        mundo = _mundo(Path(folder))
        mundo.banco.registrar(agent_id="byte", source_kind="identificacao", outcome="failure",
                              title="t", description="she thought this", content="verdict")
        wiki = Path(folder) / "WIKI.md"
        assert wiki.exists()
        texto = wiki.read_text(encoding="utf-8")
        assert "she thought this" in texto and "byte" in texto


if __name__ == "__main__":
    test_recall_reaches_mystique_and_not_the_judge()
    test_usage_count_only_grows_when_the_trace_is_actually_reused()
    test_the_wiki_is_written_next_to_the_bank()
    print("OK    bank: recall reaches Mystique, never the judge; reuse is counted honestly")
