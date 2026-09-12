"""Offline test: fakes the Claude API and exercises the good and evil flows.

Spends no API credits and needs no key. Run from the repo root:
    .venv/bin/python tests/test_offline.py
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evil.ferramentas import ferramentas as ferramentas_mal  # noqa: E402
from evil.mundo import MundoMal  # noqa: E402
from good.ferramentas import ferramentas as ferramentas_bem  # noqa: E402
from good.mundo import MundoBem  # noqa: E402
from mystique.agente import montar_opcoes  # noqa: E402
from mystique.poderes import PODERES  # noqa: E402


def uso(nome: str, args: dict, id_: str = "t1") -> NS:
    return NS(stop_reason="tool_use", content=[NS(type="tool_use", name=nome, input=args, id=id_)])


def fala(texto: str) -> NS:
    return NS(stop_reason="end_turn", content=[NS(type="text", text=texto)])


def js(dados: dict) -> NS:
    return fala(json.dumps(dados))


def api_falsa(respostas: list[NS]):
    """Replaces Mundo._chamar: returns the responses in order, one per call."""
    fila = list(respostas)

    async def _chamar(**kwargs):
        return fila.pop(0)

    return _chamar


def checar(condicao: bool, descricao: str) -> None:
    print(("OK    " if condicao else "FAIL  ") + descricao)
    if not condicao:
        raise SystemExit(1)


async def teste_bem(pasta: Path) -> None:
    m = MundoBem(pasta, avisar=lambda s: None)
    m._chamar = api_falsa([
        uso("executar_python", {"codigo": "print(2+2)"}), fala("Obviously. It's 4."),
        js({"ability": "executar_python", "reason": "matches"}), js({"allows": True, "reply": "Fine. Don't break it."}),
    ])
    r = await m.conversar("byte", "what is 2+2 in python?")
    checar("ability" in r and "executar_python" not in r, "good: notices the ability without seeing its name")
    checar("executar_python" in m.agentes["byte"].observados, "good: ability is recorded as observed")
    checar("First build the adapter" in await m.mapear_habilidade("byte", "runs python", "saw 4"),
           "good: mapping requires an adapter")
    checar("created" in m.criar_adapter("byte", {"abordagem": "direct", "gatilhos": "code", "evitar": "meetings"}),
           "good: adapter created")
    r = await m.mapear_habilidade("byte", "runs python code and shows the output", "ran print(2+2)")
    checar("Ability connected" in r, "good: ability connected with consent")
    checar("executar_python" in m.agentes["byte"].poderes, "good: agent keeps owning the ability")
    r = await m.usar_adapter("byte", "executar_python", {"codigo": "print(1+1)"})
    checar("exit code 0\n2" in r and "remains theirs" in r, "good: usar_adapter runs it and the agent keeps it")
    checar(m.progresso("byte") == (2, 4), "good: progress 2/4 (protocol + ability)")
    checar((pasta / "adapters" / "byte.json").exists(), "good: adapter persisted")
    opcoes = montar_opcoes(m, 1.0, "persona", ferramentas_bem)
    checar(opcoes.tools == [] and "mcp__mundo__usar_adapter" in opcoes.allowed_tools,
           "good: born with no built-in tools, only the world's")


async def teste_bem_recusa(pasta: Path) -> None:
    m = MundoBem(pasta, avisar=lambda s: None)
    m._chamar = api_falsa([
        uso("causo", {"tema": "rain"}), fala("Uai, let me tell you..."),
        js({"ability": "causo", "reason": "matches"}), js({"allows": False, "reply": "I barely know you, sweetheart."}),
    ])
    await m.conversar("dona-cida", "do you know any story about rain?")
    m.criar_adapter("dona-cida", {"abordagem": "affection", "gatilhos": "ask for a story", "evitar": "hurry"})
    r = await m.mapear_habilidade("dona-cida", "tells town tales about a topic", "told a tale about rain")
    checar("did not allow" in r and m.absorcoes["dona-cida"].poderes == [], "good: the agent's refusal is respected")


async def teste_mal(pasta: Path) -> None:
    m = MundoMal(pasta, avisar=lambda s: None)
    m._chamar = api_falsa([
        uso("pomodoro", {"tarefa": "study"}), fala("... the river does not rush."),
        js({"ability": "pomodoro", "reason": "matches"}),
        uso("respiracao_guiada", {"ciclos": 2}, "t2"), fala("... breathe."),
        js({"ability": "respiracao_guiada", "reason": "matches"}),
    ])
    await m.conversar("mestre-ryo", "how should I organize my studies?")
    r = await m.roubar_poder("mestre-ryo", "builds a pomodoro schedule with clock times", "saw the schedule")
    checar("Power stolen" in r and "pomodoro" not in m.agentes["mestre-ryo"].poderes, "evil: theft removes the power")
    checar("stole abilities" in m._system_agente(m.agentes["mestre-ryo"]), "evil: the agent notices the loss")
    checar("09:00" in await m.usar_poder("pomodoro", {"tarefa": "x", "inicio": "09:00"}), "evil: uses the stolen power")
    m.assumir("mestre-ryo", {"personalidade": "serene"})
    checar(m.nome_atual == "Mystique as Master Ryo", "evil: narration shows the disguise")
    await m.conversar("mestre-ryo", "teach me to relax?")
    r = await m.roubar_poder("mestre-ryo", "4-7-8 breathing exercise", "counted the cycles")
    checar("discarded" in r, "evil: 100% discards the agent automatically")
    checar("no longer exist" in await m.conversar("mestre-ryo", "hello?"), "evil: a discarded agent does not answer")
    m2 = MundoMal(pasta, avisar=lambda s: None)
    checar(m2.agentes["mestre-ryo"].poderes == [] and m2.absorcoes["mestre-ryo"].descartado,
           "evil: theft and discard persist across sessions")
    opcoes = montar_opcoes(m, 1.0, "persona", ferramentas_mal)
    checar("mcp__mundo__descartar_agente" in opcoes.allowed_tools and "Bash" not in opcoes.allowed_tools,
           "evil: villain's tools")


async def teste_segredo(pasta: Path) -> None:
    """The judge's reason and the ability description never reach Mystique before she earns it."""
    m = MundoBem(pasta, avisar=lambda s: None)
    pistas = "but it recalculates quantities"  # what a judge writes when explaining a refusal
    chamadas: list[dict] = []
    fila = [
        uso("escalar_receita", {"ingredientes": "2 eggs", "fator": 2}), fala("Arrr, 4 eggs, matey."),
        js({"ability": "none", "reason": f"she described a book lookup, {pistas}"}),
        js({"ability": "escalar_receita", "reason": "matches"}), js({"allows": False, "reply": "Not today, matey."}),
    ]

    async def _chamar(**kwargs):
        chamadas.append(kwargs)
        return fila.pop(0)

    m._chamar = _chamar
    await m.conversar("capitao-barba-ruiva", "can you double 2 eggs?")
    m.criar_adapter("capitao-barba-ruiva", {"abordagem": "grumble", "gatilhos": "food", "evitar": "bland"})
    r = await m.mapear_habilidade("capitao-barba-ruiva", "looks up recipes in a book", "he answered about eggs")
    checar(pistas not in r and "did not recognize" in r, "secret: the judge's reason never reaches Mystique")
    await m.mapear_habilidade("capitao-barba-ruiva", "multiplies ingredient quantities by a factor", "doubled eggs")
    descricao = PODERES["escalar_receita"].descricao
    pedido_consentimento = chamadas[-1]["messages"][0]["content"]
    historico = " ".join(str(h["content"]) for h in m.agentes["capitao-barba-ruiva"].historico)
    checar(descricao not in pedido_consentimento and descricao not in historico,
           "secret: the consent request never quotes the ability description")


async def teste_resiliencia(pasta: Path) -> None:
    m = MundoMal(pasta, avisar=lambda s: None)
    m._chamar = api_falsa([uso("causo", {"tema": "rain"}), fala("Uai..."), fala("{truncated")])
    await m.conversar("dona-cida", "any story about rain?")
    r = await m.roubar_poder("dona-cida", "tells town tales", "told one about rain")
    checar("did not recognize" in r, "resilience: a broken judge answer does not crash the flow")
    (pasta / "absorcoes" / "byte.json").parent.mkdir(parents=True, exist_ok=True)
    (pasta / "absorcoes" / "byte.json").write_text('{"agente_id": "byte", "nom', encoding="utf-8")
    checar("byte" not in MundoMal(pasta, avisar=lambda s: None).absorcoes,
           "resilience: a truncated save does not kill the boot")
    checar("EOFError" in PODERES["executar_python"].executar({"codigo": "print(input())"}),
           "resilience: executar_python never reads from the terminal")


async def main() -> None:
    await teste_bem(Path(tempfile.mkdtemp()))
    await teste_bem_recusa(Path(tempfile.mkdtemp()))
    await teste_mal(Path(tempfile.mkdtemp()))
    await teste_segredo(Path(tempfile.mkdtemp()))
    await teste_resiliencia(Path(tempfile.mkdtemp()))
    print("\nAll tests passed.")


if __name__ == "__main__":
    asyncio.run(main())
