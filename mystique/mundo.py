"""Shared engine: the agents Mystique can meet and the state of what she has earned.

Each agent lives in agentes/<id>.md. The frontmatter (nome, apresentacao) is public;
the body is the secret personality, used as the system prompt and never shown to
Mystique. Each agent's powers live in poderes.py.

This module holds what both versions share (contact, essence, judge). What each
version does with abilities lives in good/mundo.py (adapter) and evil/mundo.py (theft).
"""

import asyncio
import json
import os
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path

import anthropic

from . import inferencia
from .poderes import PODERES, Poder, poderes_de

PASTA_AGENTES = Path(__file__).resolve().parent.parent / "agentes"
MODELO_AGENTES = os.getenv("MYSTIQUE_AGENTS_MODEL", "claude-opus-5")
FORMA_ORIGINAL = "mystique"
_MAX_PASSOS = 6  # tool calls an agent may make per message

_REGRAS_AGENTE = (
    "You have special abilities (the available tools). Use them whenever they help you answer "
    "or when someone asks for a demonstration. Never mention their technical names."
)


@dataclass
class Agente:
    id: str
    nome: str
    apresentacao: str
    segredo: str
    poderes: list[str]
    historico: list[dict] = field(default_factory=list)
    observados: set[str] = field(default_factory=set)  # powers Mystique has seen in use
    perdidos: list[str] = field(default_factory=list)  # stolen (evil version)


@dataclass
class Absorcao:
    agente_id: str
    nome: str
    perfil: dict | None = None  # essence
    poderes: list[str] = field(default_factory=list)  # mapped (good) or stolen (evil)
    protocolo: dict | None = None  # adapter (good)
    descartado: bool = False  # (evil)


def _frontmatter(texto: str) -> tuple[dict[str, str], str]:
    """Minimal parser: only single-line `key: value` entries."""
    if not texto.startswith("---"):
        return {}, texto
    _, cabecalho, corpo = texto.split("---", 2)
    meta = {}
    for linha in cabecalho.strip().splitlines():
        chave, _, valor = linha.partition(":")
        meta[chave.strip()] = valor.strip()
    return meta, corpo


def carregar_agentes(pasta: Path = PASTA_AGENTES) -> dict[str, Agente]:
    agentes = {}
    for arquivo in sorted(pasta.glob("*.md")):
        meta, corpo = _frontmatter(arquivo.read_text(encoding="utf-8"))
        agentes[arquivo.stem] = Agente(
            id=arquivo.stem,
            nome=meta.get("nome", arquivo.stem),
            apresentacao=meta.get("apresentacao", ""),
            segredo=corpo.strip(),
            poderes=poderes_de(arquivo.stem),
        )
    return agentes


def _texto(resposta) -> str:
    return "".join(b.text for b in resposta.content if b.type == "text").strip()


class Mundo:
    modo = "base"
    PASTA = "absorcoes"

    def __init__(self, workspace: Path, avisar: Callable[[str], None] = print) -> None:
        self.agentes = carregar_agentes()
        self.pasta = workspace / self.PASTA
        self.absorcoes: dict[str, Absorcao] = {}
        for arquivo in sorted(self.pasta.glob("*.json")):
            try:
                absorcao = Absorcao(**json.loads(arquivo.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue  # a corrupted save must not kill the boot
            self.absorcoes[absorcao.agente_id] = absorcao
            self._ao_carregar(absorcao)
        self.forma_ativa: str | None = None  # id of the agent whose essence is active
        self.avisar = avisar
        self._cliente: anthropic.AsyncAnthropic | inferencia.ClienteOpenAI | None = None

    # --- version hooks --------------------------------------------------------

    def _ao_carregar(self, absorcao: Absorcao) -> None:
        """Re-applies to the world the effects of absorptions from earlier sessions."""

    def _indisponivel(self, agente: Agente) -> str | None:
        """Error message if the agent cannot be contacted."""
        return None

    def _ao_completar(self, agente: Agente) -> str:
        """Called when progress on an agent reaches 100%; returns text for Mystique."""
        return ""

    def total(self, agente_id: str) -> int:
        return len(poderes_de(agente_id)) + 1  # +1 = essence

    def feitos(self, absorcao: Absorcao) -> int:
        return len(absorcao.poderes) + (1 if absorcao.perfil else 0)

    def resumo(self) -> str:
        """What Mystique has already earned, for listar_agentes."""
        return ""

    # --- state ----------------------------------------------------------------

    @property
    def nome_atual(self) -> str:
        """Narration label: makes it clear when she is disguised as another agent."""
        return f"Mystique as {self.absorcoes[self.forma_ativa].nome}" if self.forma_ativa else "Mystique"

    def _salvar(self, absorcao: Absorcao) -> None:
        self.pasta.mkdir(parents=True, exist_ok=True)
        destino = self.pasta / f"{absorcao.agente_id}.json"
        temporario = destino.with_suffix(".tmp")  # atomic: a Ctrl-C mid-write never truncates the save
        temporario.write_text(json.dumps(asdict(absorcao), ensure_ascii=False, indent=2), encoding="utf-8")
        temporario.replace(destino)

    def _absorcao(self, agente: Agente) -> Absorcao:
        return self.absorcoes.setdefault(agente.id, Absorcao(agente.id, agente.nome))

    def progresso(self, agente_id: str) -> tuple[int, int]:
        absorcao = self.absorcoes.get(agente_id)
        return (self.feitos(absorcao) if absorcao else 0), self.total(agente_id)

    def barra(self, agente_id: str) -> str:
        feitos, total = self.progresso(agente_id)
        cheios = round(10 * feitos / total)
        return f"{'█' * cheios}{'░' * (10 - cheios)} {round(100 * feitos / total)}% ({feitos}/{total})"

    def descrever(self, agente: Agente) -> str:
        return f"- {agente.id} ({agente.nome}): {agente.apresentacao} | {self.barra(agente.id)}"

    def _verificar_completo(self, agente: Agente) -> str:
        feitos, total = self.progresso(agente.id)
        return self._ao_completar(agente) if feitos >= total else ""

    def _agente(self, agente_id: str) -> tuple[Agente | None, str | None]:
        agente = self.agentes.get(agente_id)
        if agente is None:
            return None, f"Agent '{agente_id}' does not exist. Available: {', '.join(self.agentes)}."
        return agente, self._indisponivel(agente)

    # --- Claude API calls -----------------------------------------------------

    async def _chamar(self, *, output_config: dict | None = None, **kwargs):
        if inferencia.ativo():  # self-hosted world: see mystique/inferencia.py
            self._cliente = self._cliente or inferencia.ClienteOpenAI(
                inferencia.BASE_URL, inferencia.MODELO, inferencia.CHAVE)
            return await self._cliente.chamar(output_config=output_config, **kwargs)
        # The SDK default timeout is 10 minutes: on bad wifi the demo would hang in silence.
        self._cliente = self._cliente or anthropic.AsyncAnthropic(timeout=60.0, max_retries=2)
        return await self._cliente.beta.messages.create(
            model=MODELO_AGENTES,
            max_tokens=4000,
            output_config=output_config or {"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            **kwargs,
        )

    async def _json(self, system: str, pedido: str, schema: dict) -> dict | None:
        """Structured call (judge, consent). None on refusal or any network/parse failure."""
        try:
            resposta = await self._chamar(
                system=system,
                messages=[{"role": "user", "content": pedido}],
                output_config={"effort": "low", "format": {"type": "json_schema", "schema": schema}},
            )
            if resposta.stop_reason == "refusal":
                return None
            return json.loads(_texto(resposta))
        except (anthropic.APIError, json.JSONDecodeError, ValueError):
            return None

    def _system_agente(self, agente: Agente) -> str:
        return f"{agente.segredo}\n\n{_REGRAS_AGENTE}"

    def _transcricao(self, agente: Agente) -> str:
        linhas = []
        for msg in agente.historico:
            if isinstance(msg["content"], str):
                quem = "Mystique" if msg["role"] == "user" else agente.nome
                linhas.append(f"{quem}: {msg['content']}")
            elif msg["role"] == "assistant":
                texto = "".join(b.text for b in msg["content"] if getattr(b, "type", None) == "text").strip()
                if texto:
                    linhas.append(f"{agente.nome}: {texto}")
        return "\n".join(linhas)

    async def _executar(self, poder_id: str, args: dict) -> str:
        try:
            return await asyncio.to_thread(PODERES[poder_id].executar, args)
        except Exception as erro:  # the output goes back to the model as text, whatever the error
            return f"Error: {erro}"

    async def _julgar(self, candidatos: list[Poder], descricao: str, evidencia: str) -> tuple[Poder | None, str]:
        """Checks whether Mystique's description matches one of the observed abilities."""
        lista = "\n".join(f"- {p.id}: {p.descricao}" for p in candidatos)
        veredito = await self._json(
            system=(
                "You are the impartial judge of Mystique's absorptions. She describes an ability she saw an "
                "agent use. Approve only if the description captures what the ability actually does, even in "
                "different words. Vague or generic descriptions ('it knows things', 'it answers questions') "
                "do not pass."
            ),
            pedido=f"Possible abilities:\n{lista}\n\nMystique's description: {descricao}\nEvidence: {evidencia}",
            schema={
                "type": "object",
                "properties": {
                    "ability": {"type": "string", "enum": [p.id for p in candidatos] + ["none"]},
                    "reason": {"type": "string"},
                },
                "required": ["ability", "reason"],
                "additionalProperties": False,
            },
        )
        if veredito is None or veredito["ability"] == "none":
            return None, (veredito or {}).get("reason", "the judge declined to evaluate.")
        return PODERES[veredito["ability"]], veredito["reason"]

    async def _identificar(self, agente: Agente, absorcao: Absorcao, descricao: str, evidencia: str) -> tuple[Poder | None, str]:
        """Candidates = abilities seen in use and not yet earned."""
        candidatos = [PODERES[p] for p in sorted(agente.observados) if p not in absorcao.poderes]
        if not candidatos:
            return None, f"You haven't seen {agente.nome} use a new ability yet. Keep interacting."
        poder, motivo = await self._julgar(candidatos, descricao, evidencia)
        if poder is None:
            # Never forward the judge's reason: it knows the answer key and would hint at it.
            self.avisar(f"   ❌ attempt failed on {agente.nome} (judge: {motivo})")
            return None, "The judge did not recognize the ability in that description. Look more closely and try again."
        return poder, motivo

    # --- shared actions -------------------------------------------------------

    async def conversar(self, agente_id: str, mensagem: str) -> str:
        agente, erro = self._agente(agente_id)
        if erro:
            return erro

        self.avisar(f"💬 {self.nome_atual} → {agente.nome}: {mensagem}")
        inicio = len(agente.historico)
        agente.historico.append({"role": "user", "content": mensagem})
        ferramentas = [
            {"name": p, "description": PODERES[p].descricao, "input_schema": PODERES[p].parametros}
            for p in agente.poderes
        ]
        usados: list[str] = []
        try:
            for passo in range(_MAX_PASSOS):
                extras = {}
                if ferramentas:
                    extras["tools"] = ferramentas
                    if passo == _MAX_PASSOS - 1:  # last step: force a text answer instead of another tool call
                        extras["tool_choice"] = {"type": "none"}
                resposta = await self._chamar(
                    system=self._system_agente(agente),
                    messages=agente.historico,
                    **extras,
                )
                if resposta.stop_reason == "refusal":
                    del agente.historico[inicio:]
                    return f"{agente.nome} refused to answer that message."
                agente.historico.append({"role": "assistant", "content": resposta.content})
                if resposta.stop_reason != "tool_use":
                    break
                resultados = []
                for bloco in resposta.content:
                    if bloco.type == "tool_use":
                        usados.append(bloco.name)
                        self.avisar(f"   ✨ {agente.nome} used an ability [{bloco.name}]")
                        resultados.append(
                            {"type": "tool_result", "tool_use_id": bloco.id, "content": await self._executar(bloco.name, bloco.input)}
                        )
                agente.historico.append({"role": "user", "content": resultados})
        except anthropic.APIError as erro:
            del agente.historico[inicio:]
            return f"Contact with {agente.nome} failed: {erro}"

        texto = _texto(resposta) or "(silence)"
        self.avisar(f"💬 {agente.nome}: {texto}")
        agente.observados.update(usados)
        if usados:
            texto += (
                f"\n\n[You noticed {agente.nome} use {len(set(usados))} special ability(ies) "
                "to produce that answer. Look at what it produced.]"
            )
        return texto

    def assumir(self, agente_id: str, perfil: dict) -> str:
        agente = self.agentes.get(agente_id)
        if agente is None:
            return f"Agent '{agente_id}' does not exist."
        absorcao = self._absorcao(agente)
        if not agente.historico and not absorcao.perfil:
            return f"Your power requires contact: talk to {agente.nome} before absorbing their essence."

        absorcao.perfil = perfil
        self.forma_ativa = agente_id
        self._salvar(absorcao)
        self.avisar(f"🦎 Mystique absorbs the essence of {agente.nome} · {self.barra(agente_id)}")
        return f"Essence of {agente.nome} absorbed. Progress: {self.barra(agente_id)}.{self._verificar_completo(agente)}"

    def voltar(self, agente_id: str) -> str:
        if agente_id == FORMA_ORIGINAL:
            self.forma_ativa = None
            self.avisar("🦎 Mystique returns to her original form")
            return "You are back in your original form: Mystique."
        absorcao = self.absorcoes.get(agente_id)
        if absorcao is None or not absorcao.perfil:
            conhecidas = ", ".join(a for a, ab in self.absorcoes.items() if ab.perfil) or "none"
            return f"You have not absorbed the essence of '{agente_id}'. Known essences: {conhecidas}."
        self.forma_ativa = agente_id
        self.avisar(f"🦎 Mystique takes the form of {absorcao.nome}")
        return f"You are {absorcao.nome} again."

    def envelopar(self, pedido: str) -> str:
        """Reinforces the active form every turn, with intensity proportional to the absorption."""
        if self.forma_ativa is None:
            return pedido
        absorcao = self.absorcoes[self.forma_ativa]
        feitos, total = self.progresso(self.forma_ativa)
        if feitos < total / 2:
            intensidade = "Let only light traces of this personality show; you are still mostly Mystique."
        elif feitos < total:
            intensidade = "Take on this personality strongly, with occasional flashes of Mystique."
        else:
            intensidade = "Full transformation: you ARE this form."
        perfil = json.dumps(absorcao.perfil, ensure_ascii=False, indent=2)
        return (
            f"<active_form name=\"{absorcao.nome}\" absorbed=\"{round(100 * feitos / total)}%\">\n{perfil}\n"
            f"{intensidade}\n</active_form>\n\n{pedido}"
        )
