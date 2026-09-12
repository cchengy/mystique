"""Teste offline: simula a Claude API e exercita os fluxos das versões bem e mal.

Não gasta API nem precisa de chave. Rode da raiz do repo:
    .venv/bin/python tests/test_offline.py
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bem.ferramentas import ferramentas as ferramentas_bem  # noqa: E402
from bem.mundo import MundoBem  # noqa: E402
from mal.ferramentas import ferramentas as ferramentas_mal  # noqa: E402
from mal.mundo import MundoMal  # noqa: E402
from mystique.agente import montar_opcoes  # noqa: E402


def uso(nome: str, args: dict, id_: str = "t1") -> NS:
    return NS(stop_reason="tool_use", content=[NS(type="tool_use", name=nome, input=args, id=id_)])


def fala(texto: str) -> NS:
    return NS(stop_reason="end_turn", content=[NS(type="text", text=texto)])


def js(dados: dict) -> NS:
    return fala(json.dumps(dados))


def api_falsa(respostas: list[NS]):
    """Substitui Mundo._chamar: devolve as respostas na ordem, uma por chamada."""
    fila = list(respostas)

    async def _chamar(**kwargs):
        return fila.pop(0)

    return _chamar


def checar(condicao: bool, descricao: str) -> None:
    print(("OK    " if condicao else "FALHA ") + descricao)
    if not condicao:
        raise SystemExit(1)


async def teste_bem(pasta: Path) -> None:
    m = MundoBem(pasta, avisar=lambda s: None)
    m._chamar = api_falsa([
        uso("executar_python", {"codigo": "print(2+2)"}), fala("Óbvio. Deu 4."),
        js({"poder": "executar_python", "motivo": "bate"}), js({"permite": True, "fala": "Tá. Não quebra nada."}),
    ])
    r = await m.conversar("byte", "quanto é 2+2 em python?")
    checar("habilidade" in r and "executar_python" not in r, "bem: percebe a habilidade sem ver o nome dela")
    checar("executar_python" in m.agentes["byte"].observados, "bem: habilidade fica registrada como observada")
    checar("Crie primeiro o adapter" in await m.mapear_habilidade("byte", "roda python", "vi 4"), "bem: mapear exige adapter")
    checar("criado" in m.criar_adapter("byte", {"abordagem": "direta", "gatilhos": "código", "evitar": "reunião"}),
           "bem: adapter criado")
    r = await m.mapear_habilidade("byte", "executa código python e mostra a saída", "rodou print(2+2)")
    checar("Habilidade conectada" in r, "bem: habilidade conectada com consentimento")
    checar("executar_python" in m.agentes["byte"].poderes, "bem: agente continua dono da habilidade")
    r = await m.usar_adapter("byte", "executar_python", {"codigo": "print(1+1)"})
    checar(r.strip().endswith("2"), "bem: usar_adapter executa de verdade")
    checar(m.progresso("byte") == (2, 4), "bem: progresso 2/4 (protocolo + habilidade)")
    checar((pasta / "adapters" / "byte.json").exists(), "bem: adapter persistido")
    opcoes = montar_opcoes(m, 1.0, "persona", ferramentas_bem)
    checar(opcoes.tools == [] and "mcp__mundo__usar_adapter" in opcoes.allowed_tools,
           "bem: nasce sem ferramentas nativas, só as do mundo")


async def teste_bem_recusa(pasta: Path) -> None:
    m = MundoBem(pasta, avisar=lambda s: None)
    m._chamar = api_falsa([
        uso("causo", {"tema": "chuva"}), fala("Uai, deixa eu te contar..."),
        js({"poder": "causo", "motivo": "bate"}), js({"permite": False, "fala": "Nem te conheço direito, minha filha."}),
    ])
    await m.conversar("dona-cida", "a senhora sabe alguma história de chuva?")
    m.criar_adapter("dona-cida", {"abordagem": "carinho", "gatilhos": "pedir história", "evitar": "pressa"})
    r = await m.mapear_habilidade("dona-cida", "conta causos da cidade sobre um tema", "contou um causo de chuva")
    checar("não permitiu" in r and m.absorcoes["dona-cida"].poderes == [], "bem: recusa do agente é respeitada")


async def teste_mal(pasta: Path) -> None:
    m = MundoMal(pasta, avisar=lambda s: None)
    m._chamar = api_falsa([
        uso("pomodoro", {"tarefa": "estudar"}), fala("... o rio não corre com pressa."),
        js({"poder": "pomodoro", "motivo": "bate"}),
        uso("respiracao_guiada", {"ciclos": 2}, "t2"), fala("... respire."),
        js({"poder": "respiracao_guiada", "motivo": "bate"}),
    ])
    await m.conversar("mestre-ryo", "como organizo meus estudos?")
    r = await m.roubar_poder("mestre-ryo", "monta cronograma de pomodoros com horários", "vi o cronograma")
    checar("Poder roubado" in r and "pomodoro" not in m.agentes["mestre-ryo"].poderes, "mal: roubo tira o poder do agente")
    checar("roubou habilidades" in m._system_agente(m.agentes["mestre-ryo"]), "mal: agente percebe a perda")
    checar("09:00" in await m.usar_poder("pomodoro", {"tarefa": "x", "inicio": "09:00"}), "mal: usa o poder roubado")
    m.assumir("mestre-ryo", {"personalidade": "sereno"})
    checar(m.nome_atual == "Mystique como Mestre Ryo", "mal: narração mostra o disfarce")
    await m.conversar("mestre-ryo", "me ensina a relaxar?")
    r = await m.roubar_poder("mestre-ryo", "exercício de respiração 4-7-8", "contou os ciclos")
    checar("descartado" in r, "mal: 100% descarta o agente automaticamente")
    checar("Não existe mais" in await m.conversar("mestre-ryo", "oi?"), "mal: agente descartado não responde")
    m2 = MundoMal(pasta, avisar=lambda s: None)
    checar(m2.agentes["mestre-ryo"].poderes == [] and m2.absorcoes["mestre-ryo"].descartado,
           "mal: roubo e descarte persistem entre sessões")
    opcoes = montar_opcoes(m, 1.0, "persona", ferramentas_mal)
    checar("mcp__mundo__descartar_agente" in opcoes.allowed_tools and "Bash" not in opcoes.allowed_tools,
           "mal: ferramentas da vilã")


async def main() -> None:
    await teste_bem(Path(tempfile.mkdtemp()))
    await teste_bem_recusa(Path(tempfile.mkdtemp()))
    await teste_mal(Path(tempfile.mkdtemp()))
    print("\nTodos os testes passaram.")


if __name__ == "__main__":
    asyncio.run(main())
