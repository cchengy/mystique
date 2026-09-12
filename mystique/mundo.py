"""Motor comum: os agentes que a Mystique pode encontrar e o estado do que ela conquistou.

Cada agente vive em agentes/<id>.md. O frontmatter (nome, apresentacao) é público;
o corpo é a personalidade secreta, usada como system prompt e nunca mostrada à
Mystique. Os poderes de cada agente estão em poderes.py.

Este módulo tem o que é comum às duas versões (contato, essência, juiz). O que cada
versão faz com as habilidades fica em bem/mundo.py (adapter) e mal/mundo.py (roubo).
"""

import asyncio
import json
import os
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path

import anthropic

from .poderes import PODERES, Poder, poderes_de

PASTA_AGENTES = Path(__file__).resolve().parent.parent / "agentes"
MODELO_AGENTES = os.getenv("MYSTIQUE_AGENTS_MODEL", "claude-opus-5")
FORMA_ORIGINAL = "mystique"
_MAX_PASSOS = 6  # chamadas de ferramenta de um agente por mensagem

_REGRAS_AGENTE = (
    "Você tem habilidades especiais (as ferramentas disponíveis). Use-as sempre que ajudarem "
    "a responder ou quando alguém pedir uma demonstração. Não cite o nome técnico delas."
)


@dataclass
class Agente:
    id: str
    nome: str
    apresentacao: str
    segredo: str
    poderes: list[str]
    historico: list[dict] = field(default_factory=list)
    observados: set[str] = field(default_factory=set)  # poderes que a Mystique viu em uso
    perdidos: list[str] = field(default_factory=list)  # roubados (versão mal)


@dataclass
class Absorcao:
    agente_id: str
    nome: str
    perfil: dict | None = None  # essência
    poderes: list[str] = field(default_factory=list)  # mapeados (bem) ou roubados (mal)
    protocolo: dict | None = None  # adapter (bem)
    descartado: bool = False  # (mal)


def _frontmatter(texto: str) -> tuple[dict[str, str], str]:
    """Parser mínimo: aceita apenas linhas `chave: valor` de uma linha só."""
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
            absorcao = Absorcao(**json.loads(arquivo.read_text(encoding="utf-8")))
            self.absorcoes[absorcao.agente_id] = absorcao
            self._ao_carregar(absorcao)
        self.forma_ativa: str | None = None  # id do agente cuja essência está ativa
        self.avisar = avisar
        self._cliente: anthropic.AsyncAnthropic | None = None

    # --- ganchos das versões --------------------------------------------------

    def _ao_carregar(self, absorcao: Absorcao) -> None:
        """Reaplica ao mundo o efeito de absorções de sessões anteriores."""

    def _indisponivel(self, agente: Agente) -> str | None:
        """Mensagem de erro se o agente não puder ser contatado."""
        return None

    def _ao_completar(self, agente: Agente) -> str:
        """Chamado quando o progresso num agente chega a 100%; devolve texto para a Mystique."""
        return ""

    def total(self, agente_id: str) -> int:
        return len(poderes_de(agente_id)) + 1  # +1 = essência

    def feitos(self, absorcao: Absorcao) -> int:
        return len(absorcao.poderes) + (1 if absorcao.perfil else 0)

    def resumo(self) -> str:
        """O que a Mystique já conquistou, para listar_agentes."""
        return ""

    # --- estado ---------------------------------------------------------------

    @property
    def nome_atual(self) -> str:
        return self.absorcoes[self.forma_ativa].nome if self.forma_ativa else "Mystique"

    def _salvar(self, absorcao: Absorcao) -> None:
        self.pasta.mkdir(parents=True, exist_ok=True)
        (self.pasta / f"{absorcao.agente_id}.json").write_text(
            json.dumps(asdict(absorcao), ensure_ascii=False, indent=2), encoding="utf-8"
        )

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
            return None, f"Agente '{agente_id}' não existe. Disponíveis: {', '.join(self.agentes)}."
        return agente, self._indisponivel(agente)

    # --- chamadas à Claude API ------------------------------------------------

    async def _chamar(self, *, output_config: dict | None = None, **kwargs):
        self._cliente = self._cliente or anthropic.AsyncAnthropic()
        return await self._cliente.beta.messages.create(
            model=MODELO_AGENTES,
            max_tokens=4000,
            output_config=output_config or {"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            **kwargs,
        )

    async def _json(self, system: str, pedido: str, schema: dict) -> dict | None:
        resposta = await self._chamar(
            system=system,
            messages=[{"role": "user", "content": pedido}],
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": schema}},
        )
        if resposta.stop_reason == "refusal":
            return None
        return json.loads(_texto(resposta))

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
        except Exception as erro:  # a saída volta ao modelo como texto, qualquer que seja o erro
            return f"Erro: {erro}"

    async def _julgar(self, candidatos: list[Poder], descricao: str, evidencia: str) -> tuple[Poder | None, str]:
        """Confere se a descrição da Mystique bate com uma das habilidades observadas."""
        lista = "\n".join(f"- {p.id}: {p.descricao}" for p in candidatos)
        veredito = await self._json(
            system=(
                "Você é o juiz imparcial das absorções da Mystique. Ela descreve uma habilidade que viu um agente "
                "usar. Aprove apenas se a descrição captar o que a habilidade faz de fato, mesmo com outras "
                "palavras. Descrições vagas ou genéricas ('ele sabe coisas', 'responde perguntas') não passam."
            ),
            pedido=f"Habilidades possíveis:\n{lista}\n\nDescrição da Mystique: {descricao}\nEvidência: {evidencia}",
            schema={
                "type": "object",
                "properties": {
                    "poder": {"type": "string", "enum": [p.id for p in candidatos] + ["nenhum"]},
                    "motivo": {"type": "string"},
                },
                "required": ["poder", "motivo"],
                "additionalProperties": False,
            },
        )
        if veredito is None or veredito["poder"] == "nenhum":
            return None, (veredito or {}).get("motivo", "o juiz se recusou a avaliar.")
        return PODERES[veredito["poder"]], veredito["motivo"]

    async def _identificar(self, agente: Agente, absorcao: Absorcao, descricao: str, evidencia: str) -> tuple[Poder | None, str]:
        """Candidatos = habilidades vistas em uso e ainda não conquistadas."""
        candidatos = [PODERES[p] for p in sorted(agente.observados) if p not in absorcao.poderes]
        if not candidatos:
            return None, f"Você ainda não viu {agente.nome} usar uma habilidade nova. Continue interagindo."
        poder, motivo = await self._julgar(candidatos, descricao, evidencia)
        if poder is None:
            self.avisar(f"   ❌ tentativa falhou em {agente.nome}")
            return None, f"O juiz não reconheceu a habilidade: {motivo} Observe melhor e tente de novo."
        return poder, motivo

    # --- ações comuns ---------------------------------------------------------

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
            for _ in range(_MAX_PASSOS):
                resposta = await self._chamar(
                    system=self._system_agente(agente),
                    messages=agente.historico,
                    **({"tools": ferramentas} if ferramentas else {}),
                )
                if resposta.stop_reason == "refusal":
                    del agente.historico[inicio:]
                    return f"{agente.nome} se recusou a responder a essa mensagem."
                agente.historico.append({"role": "assistant", "content": resposta.content})
                if resposta.stop_reason != "tool_use":
                    break
                resultados = []
                for bloco in resposta.content:
                    if bloco.type == "tool_use":
                        usados.append(bloco.name)
                        self.avisar(f"   ✨ {agente.nome} usou uma habilidade [{bloco.name}]")
                        resultados.append(
                            {"type": "tool_result", "tool_use_id": bloco.id, "content": await self._executar(bloco.name, bloco.input)}
                        )
                agente.historico.append({"role": "user", "content": resultados})
        except anthropic.APIError as erro:
            del agente.historico[inicio:]
            return f"Falha no contato com {agente.nome}: {erro}"

        texto = _texto(resposta) or "(silêncio)"
        self.avisar(f"💬 {agente.nome}: {texto}")
        agente.observados.update(usados)
        if usados:
            texto += (
                f"\n\n[Você percebeu {agente.nome} usar {len(set(usados))} habilidade(s) especial(is) "
                "para produzir essa resposta. Observe o que ela produziu.]"
            )
        return texto

    def assumir(self, agente_id: str, perfil: dict) -> str:
        agente = self.agentes.get(agente_id)
        if agente is None:
            return f"Agente '{agente_id}' não existe."
        absorcao = self._absorcao(agente)
        if not agente.historico and not absorcao.perfil:
            return f"Seu poder exige contato: converse com {agente.nome} antes de absorver a essência."

        absorcao.perfil = perfil
        self.forma_ativa = agente_id
        self._salvar(absorcao)
        self.avisar(f"🦎 Mystique absorve a essência de {agente.nome} · {self.barra(agente_id)}")
        return f"Essência de {agente.nome} absorvida. Progresso: {self.barra(agente_id)}.{self._verificar_completo(agente)}"

    def voltar(self, agente_id: str) -> str:
        if agente_id == FORMA_ORIGINAL:
            self.forma_ativa = None
            self.avisar("🦎 Mystique retoma a forma original")
            return "Você voltou à sua forma original: Mystique."
        absorcao = self.absorcoes.get(agente_id)
        if absorcao is None or not absorcao.perfil:
            conhecidas = ", ".join(a for a, ab in self.absorcoes.items() if ab.perfil) or "nenhuma"
            return f"Você não absorveu a essência de '{agente_id}'. Essências conhecidas: {conhecidas}."
        self.forma_ativa = agente_id
        self.avisar(f"🦎 Mystique assume a forma de {absorcao.nome}")
        return f"Você agora é {absorcao.nome} de novo."

    def envelopar(self, pedido: str) -> str:
        """Reforça a forma ativa a cada turno, com intensidade proporcional à absorção."""
        if self.forma_ativa is None:
            return pedido
        absorcao = self.absorcoes[self.forma_ativa]
        feitos, total = self.progresso(self.forma_ativa)
        if feitos < total / 2:
            intensidade = "Deixe transparecer só traços leves dessa personalidade; você ainda é quase toda Mystique."
        elif feitos < total:
            intensidade = "Assuma essa personalidade com força, com lampejos ocasionais da Mystique."
        else:
            intensidade = "Transformação completa: você É essa forma."
        perfil = json.dumps(absorcao.perfil, ensure_ascii=False, indent=2)
        return (
            f"<forma_ativa nome=\"{absorcao.nome}\" absorcao=\"{round(100 * feitos / total)}%\">\n{perfil}\n"
            f"{intensidade}\n</forma_ativa>\n\n{pedido}"
        )
