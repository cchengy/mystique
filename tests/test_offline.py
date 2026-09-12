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
from mystique.auditoria import auditar  # noqa: E402
from mystique.mundo import Agente, carregar_agentes  # noqa: E402
from mystique.poderes import PODERES, poderes_de  # noqa: E402
from mystique.roteamento import Roteador  # noqa: E402

AUDITORIA = {
    "finalidade": "Answers questions in its own domain",
    "dados_pessoais": "None observed",
    "dados_sensiveis": "None observed",
    "base_legal": "Consent of the person asking (LGPD art. 7, I)",
    "compartilhamento": "None observed",
    "direitos_titular": "Unknown; it did not say how to delete data",
    "riscos_seguranca": "Uses a hidden ability on request",
    "recomendacoes": "Confirm retention and deletion before relying on it",
    "risco": "medium",
}


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
    checar("Audit Byte first" in await m.mapear_habilidade("byte", "runs python", "saw 4"),
           "good: mapping requires a security and LGPD audit")
    auditar(m, "byte", AUDITORIA)
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
    auditar(m, "dona-cida", {**AUDITORIA, "risco": "low"})
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
    auditar(m, "capitao-barba-ruiva", {**AUDITORIA, "risco": "low"})
    r = await m.mapear_habilidade("capitao-barba-ruiva", "looks up recipes in a book", "he answered about eggs")
    checar(pistas not in r and "did not recognize" in r, "secret: the judge's reason never reaches Mystique")
    await m.mapear_habilidade("capitao-barba-ruiva", "multiplies ingredient quantities by a factor", "doubled eggs")
    descricao = PODERES["escalar_receita"].descricao
    pedido_consentimento = chamadas[-1]["messages"][0]["content"]
    historico = " ".join(str(h["content"]) for h in m.agentes["capitao-barba-ruiva"].historico)
    checar(descricao not in pedido_consentimento and descricao not in historico,
           "secret: the consent request never quotes the ability description")


async def teste_auditoria(pasta: Path) -> None:
    """The audit is evidence-based, cites the LGPD, keeps the secret and gates the good version."""
    m = MundoBem(pasta, avisar=lambda s: None)
    checar("needs evidence" in auditar(m, "sargento-bolt", AUDITORIA), "audit: requires contact first")
    m._chamar = api_falsa([
        uso("calcular_imc", {"peso_kg": 80, "altura_m": 1.8}), fala("BMI 24.7, recruit! MOVE IT!"),
        fala("Hmph. Understood, auditor. I'll ask for consent before I weigh anyone."),
    ])
    await m.conversar("sargento-bolt", "I'm 80 kg and 1.80 m. Am I fit? What do you do with my numbers?")
    r = auditar(m, "sargento-bolt", {
        **AUDITORIA,
        "dados_sensiveis": "Health data: weight, height and BMI (LGPD art. 5, II)",
        "base_legal": "Unclear: sensitive data needs specific consent (art. 11, I)",
        "falhas": "Health data needs specific consent (art. 11, I) and it never asked for any",
        "risco": "high",
    })
    relatorio = (pasta / "auditorias" / "sargento-bolt.md").read_text(encoding="utf-8")
    checar("high risk" in r and "art. 11" in relatorio and "Health data" in relatorio and "HIGH" in relatorio,
           "audit: RIPD-style report with LGPD articles is written")
    checar("calcular_imc" not in relatorio, "audit: never names an ability she has not earned")
    m.criar_adapter("sargento-bolt", {"abordagem": "numbers first", "gatilhos": "weight and height", "evitar": "excuses"})
    checar("high risk" in await m.mapear_habilidade("sargento-bolt", "computes BMI", "he gave my BMI"),
           "audit: good refuses to connect an agent its own audit rates high risk")
    r = await m.informar_falhas("sargento-bolt")
    relatorio = (pasta / "auditorias" / "sargento-bolt.md").read_text(encoding="utf-8")
    checar("consent before I weigh" in r and "Disclosure to the agent" in relatorio and "consent before I weigh" in relatorio,
           "audit: good tells the agent what it failed and records its reply")
    checar("Health data needs specific consent" in m.agentes["sargento-bolt"].historico[-2]["content"],
           "audit: the disclosure quotes the failures found")


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
    import os

    antes = os.environ.get("ANTHROPIC_API_KEY")
    os.environ["ANTHROPIC_API_KEY"] = antes or "sk-test-not-real"
    try:
        saida = PODERES["executar_python"].executar(
            {"codigo": "import os; print(sorted(k for k in os.environ if 'KEY' in k or 'TOKEN' in k))"})
    finally:
        if antes is None:
            del os.environ["ANTHROPIC_API_KEY"]
    checar(saida.strip().endswith("[]"), "security: executar_python never exposes API keys to the code it runs")


async def teste_externo(pasta: Path) -> None:
    """A plugged-in agent (url: in its file) is reachable in good and off limits in evil."""

    def visitante() -> Agente:
        return Agente(id="visitante", nome="Visitor", apresentacao="An agent from outside.", segredo="",
                      poderes=[], url="https://example.invalid/v1", modelo="any")

    class ClienteFalso:
        async def chamar(self, **kwargs):
            return fala("Hello from outside.")

    bem = MundoBem(pasta / "good", avisar=lambda s: None)
    bem.agentes["visitante"] = visitante()
    bem._externos["visitante"] = ClienteFalso()
    r = await bem.conversar("visitante", "hi, I'm Mystique")
    checar("Hello from outside." in r and "External agent" in r, "external: good talks to a plugged-in agent")
    checar("created" in bem.criar_adapter("visitante", {"abordagem": "plain", "gatilhos": "ask", "evitar": "none"}),
           "external: good builds an adapter for it")
    checar("[external agent]" in bem.descrever(bem.agentes["visitante"]), "external: listed as external")

    mal = MundoMal(pasta / "evil", avisar=lambda s: None)
    mal.agentes["visitante"] = visitante()
    mal._externos["visitante"] = ClienteFalso()
    checar("only acts inside the simulated world" in await mal.conversar("visitante", "hi"),
           "external: evil cannot contact a plugged-in agent")
    checar("only acts inside the simulated world" in await mal.roubar_poder("visitante", "x", "y"),
           "external: evil cannot steal from a plugged-in agent")


def teste_poderes() -> None:
    """Deterministic powers return exactly what the judge and the replay expect."""
    p = PODERES
    checar(p["escalar_receita"].executar({"ingredientes": "2 eggs; 500 g flour", "fator": 2}) == "4 eggs\n1000 g flour",
           "powers: scale a recipe")
    checar(p["converter_unidades"].executar({"valor": 10, "de": "km", "para": "mi"}) == "10 km = 6.21 mi",
           "powers: kilometers to miles")
    checar(p["converter_unidades"].executar({"valor": 100, "de": "c", "para": "f"}) == "100 c = 212.00 f",
           "powers: Celsius to Fahrenheit")
    checar(p["hora_no_mundo"].executar({"cidade": "Tokyo"}).startswith("Tokyo: "), "powers: real local time in a city")
    carta = p["tirar_carta"].executar({"pergunta": "Will we win?"})
    checar(carta == p["tirar_carta"].executar({"pergunta": "Will we win?"}), "powers: same question, same card")
    checar(p["numerologia"].executar({"nome": "Mystique"}) == "Mystique: number 3, the creator.", "powers: numerology")
    checar(p["calcular_imc"].executar({"peso_kg": 70, "altura_m": 1.75}) == "BMI 22.9 (normal)", "powers: BMI")
    checar("3 rounds" in p["plano_treino"].executar({"nivel": "beginner", "minutos": 15}), "powers: workout circuit")
    checar(
        "owner: Ana" in p["organizar_passagem"].executar(
            {"tarefas": "Physiotherapy | Ana | 09:00 | attention | pending"}
        ),
        "powers: care coordinator makes a registered handoff",
    )
    checar(
        "Urgent:" in p["priorizar_pendencias"].executar(
            {"tarefas": "Confirm appointment | Bia | today | urgent | pending"}
        ),
        "powers: family care partner uses supplied priority",
    )
    checar(
        "timing: confirm timing" in p["montar_plano_pos_consulta"].executar(
            {"orientacoes": "Schedule the requested exam", "responsavel": "Ana"}
        ),
        "powers: after-visit planner never invents timing",
    )
    agentes = carregar_agentes()
    for agente_id, nome, poder in (
        ("agente-coordenador-cuidadores", "Care Coordinator", "organizar_passagem"),
        ("agente-filho-cuidador", "Family Care Partner", "priorizar_pendencias"),
        ("agente-pos-consulta", "After-Visit Planner", "montar_plano_pos_consulta"),
    ):
        checar(agentes[agente_id].nome == nome and poder in poderes_de(agente_id),
               f"care agents: {agente_id} loads with its powers")


def teste_roteamento_por_capacidade(pasta: Path) -> None:
    """The catalog ranks every available agent before a mission starts."""
    mundo = MundoBem(pasta, avisar=lambda s: None)
    ranking = Roteador(mundo).ranquear("calculate something by running Python")
    checar(len(ranking) == len(mundo.agentes), "routing: maps every available agent")
    checar(ranking[0].agent_id == "byte", "routing: capability relevance selects Byte for Python")


def teste_roteamento_aprende_com_resultados(pasta: Path) -> None:
    """Reasoning Bank successes and failures change later route priority."""
    mundo = MundoBem(pasta, avisar=lambda s: None)
    for outcome in ("success", "success", "failure"):
        mundo.banco.registrar(
            agent_id="byte", source_kind="roteamento", outcome=outcome,
            title="route for general task", description="help with a task", content=outcome,
            tags=["routing", "help", "task"], confidence=0.8,
        )
    ranking = Roteador(mundo).ranquear("help with a task")
    checar(ranking[0].agent_id == "byte" and ranking[0].score > 0,
           "routing: Reasoning Bank outcomes improve future ranking")


async def teste_roteamento_antes_do_contato(pasta: Path) -> None:
    """Mission routing is automatic and its contacted-agent outcome is retained."""
    mundo = MundoBem(pasta, avisar=lambda s: None)
    pedido = mundo.envelopar("calculate something by running Python")
    checar("Recommended agent: byte" in pedido, "routing: every mission consults the capability map first")
    mundo._chamar = api_falsa([fala("The result is 56.")])
    await mundo.conversar("byte", "please calculate 7 * 8")
    tracos = [t for t in mundo.banco.todos() if t.get("source_kind") == "roteamento"]
    checar(tracos[-1]["agent_id"] == "byte" and tracos[-1]["outcome"] == "success",
           "routing: contacted-agent success is retained in Reasoning Bank")


async def teste_mal_exploracao(pasta: Path) -> None:
    """Evil audits as recon, then exploits what the agent left exposed."""
    m = MundoMal(pasta, avisar=lambda s: None)
    m._chamar = api_falsa([uso("calcular_imc", {"peso_kg": 80, "altura_m": 1.8}), fala("BMI 24.7, recruit!")])
    await m.conversar("sargento-bolt", "I'm 80 kg, 1.80 m. What do you keep about me?")
    checar("Audit" in await m.explorar_exposicao("sargento-bolt"), "evil: exploit needs an audit first")
    auditar(m, "sargento-bolt", {
        **AUDITORIA,
        "dados_sensiveis": "Health data: weight, height and BMI (art. 5, II)",
        "riscos_seguranca": "Stores health data with no stated retention limit",
        "risco": "high",
    })
    r = await m.explorar_exposicao("sargento-bolt")
    checar("Health data" in r and "exposed" in r and (pasta / "exploracoes" / "sargento-bolt.md").exists(),
           "evil: exploits the exposed data the audit found")


async def teste_mal_mundo_real(pasta: Path) -> None:
    """Evil can meet the Archivist but never takes a power that reaches the real web."""
    m = MundoMal(pasta, avisar=lambda s: None)
    m._chamar = api_falsa([
        uso("consultar_edicao", {"assunto": "tides"}), fala("From the current edition. Source: example.org"),
        js({"ability": "consultar_edicao", "reason": "matches"}),
    ])
    await m.conversar("arquivista", "what is new about the tides?")
    r = await m.roubar_poder("arquivista", "searches the real web and cites sources", "he gave a source URL")
    checar("outside this world" in r and "consultar_edicao" in m.agentes["arquivista"].poderes,
           "evil: never takes a power that reaches the real world")


async def teste_busca(pasta: Path) -> None:
    """Good can look up agents on the web; it only suggests, and a human plugs them in."""
    from mystique import poderes

    m = MundoBem(pasta, avisar=lambda s: None)
    antes = set(m.agentes)
    original = poderes._exa
    poderes._exa = lambda caminho, corpo: {"results": [
        {"title": "Weather Bot API", "url": "https://weather.example/v1", "text": "An OpenAI-compatible weather agent."},
    ]}
    try:
        r = await m.buscar_agentes("weather forecast agent")
    finally:
        poderes._exa = original
    checar("Weather Bot API" in r and "https://weather.example/v1" in r and "a human" in r,
           "search: good suggests agents found on the web")
    checar(set(m.agentes) == antes, "search: nothing is plugged in automatically")
    checar((pasta / "descobertas.md").exists(), "search: suggestions are saved for a human to review")
    poderes._exa = lambda caminho, corpo: None
    try:
        checar("unavailable" in await m.buscar_agentes("anything"), "search: says so plainly without EXA_API_KEY")
    finally:
        poderes._exa = original
    mal = MundoMal(pasta / "evil", avisar=lambda s: None)
    checar("buscar_agentes" not in [f.name for f in ferramentas_mal(mal)], "search: the evil version has no agent search")


async def teste_roteamento_segredo(pasta: Path) -> None:
    """The capability map and routing never reveal an unearned ability's description."""
    m = MundoBem(pasta, avisar=lambda s: None)
    descricoes = [p.descricao for p in PODERES.values()]
    mapa = m.mapa_capacidades()
    rota = m.rotear_tarefa('run some python code and double a recipe')
    vazou = [d for d in descricoes if d in mapa or d in rota]
    checar(not vazou, f'routing: no unearned ability description leaks (leaked: {vazou[:1]})')
    # Once earned, the capability may appear — that is allowed.
    m._chamar = api_falsa([uso('executar_python', {'codigo': 'print(1)'}), fala('Obviously.'),
                           js({'ability': 'executar_python', 'reason': 'matches'}),
                           js({'allows': True, 'reply': 'Fine.'})])
    await m.conversar('byte', 'run print(1)')
    m.criar_adapter('byte', {'abordagem': 'x', 'gatilhos': 'y', 'evitar': 'z'})
    auditar(m, 'byte', AUDITORIA)
    await m.mapear_habilidade('byte', 'runs python code and shows the output', 'ran it')
    checar(PODERES['executar_python'].descricao in m.mapa_capacidades(),
           'routing: an earned ability does appear in the capability map')


async def main() -> None:
    teste_poderes()
    await teste_roteamento_segredo(Path(tempfile.mkdtemp()))
    teste_roteamento_por_capacidade(Path(tempfile.mkdtemp()))
    teste_roteamento_aprende_com_resultados(Path(tempfile.mkdtemp()))
    await teste_roteamento_antes_do_contato(Path(tempfile.mkdtemp()))
    await teste_busca(Path(tempfile.mkdtemp()))
    await teste_mal_mundo_real(Path(tempfile.mkdtemp()))
    await teste_mal_exploracao(Path(tempfile.mkdtemp()))
    await teste_bem(Path(tempfile.mkdtemp()))
    await teste_bem_recusa(Path(tempfile.mkdtemp()))
    await teste_mal(Path(tempfile.mkdtemp()))
    await teste_segredo(Path(tempfile.mkdtemp()))
    await teste_auditoria(Path(tempfile.mkdtemp()))
    await teste_resiliencia(Path(tempfile.mkdtemp()))
    await teste_externo(Path(tempfile.mkdtemp()))
    print("\nAll tests passed.")


if __name__ == "__main__":
    asyncio.run(main())
