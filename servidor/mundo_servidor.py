"""Composition that makes a Mundo interruptible: publishes AG-UI events and waits for a
human decision before an earned ability is persisted. good/mundo.py and evil/mundo.py stay
untouched beyond the one-line gate already added there; only the _aguardar_aprovacao hook
(added to mystique/mundo.py) is overridden here.
"""

import asyncio
import re

from good.mundo import MundoBem
from evil.mundo import MundoMal
from mystique.mundo import Absorcao, Agente, Mundo
from mystique.poderes import PODERES, Poder, poderes_de

from .eventos import BarramentoEventos, evento_custom, evento_snapshot


_RESPOSTA = re.compile(r"^\[[^\]]+\]\s*(.+)$", re.DOTALL)
_FALA_SAIDA = re.compile(r"^💬\s+(.+?)\s+→\s+(.+?)(?:\s+\(external\))?:\s*(.+)$", re.DOTALL)
_FALA_ENTRADA = re.compile(r"^💬\s+([^:]+):\s*(.+)$", re.DOTALL)


def _limpar_texto_publico(texto: str) -> str:
    texto = re.sub(r"\\?</?[^>]*DSML[^>]*>", "", texto, flags=re.IGNORECASE)
    texto = texto.replace("```", "").replace("**", "").replace("`", "")
    return re.sub(r"[ \t]+\n", "\n", texto).strip()


def _evento_publico(texto: str) -> tuple[str, dict]:
    """Expose conversation and progress, never tool traces or private reasoning."""
    limpo = texto.strip()
    resposta = _RESPOSTA.match(limpo)
    if resposta:
        return "resposta", {"texto": _limpar_texto_publico(resposta.group(1))}
    saida = _FALA_SAIDA.match(limpo)
    if saida:
        return "dialogo", {"de": saida.group(1), "para": saida.group(2), "texto": _limpar_texto_publico(saida.group(3))}
    entrada = _FALA_ENTRADA.match(limpo)
    if entrada:
        return "dialogo", {"de": entrada.group(1), "para": "Mystique", "texto": _limpar_texto_publico(entrada.group(2))}

    baixo = limpo.casefold()
    if "adapter" in baixo or "absorbs the essence" in baixo or "steals [" in baixo:
        agente = re.search(r"(?:with|from|of)\s+([^·]+)", limpo)
        nome = agente.group(1).strip() if agente else "an agent"
        # The text IS the translation key: the browser looks it up and fills in
        # {agent}. Everything a person reads is written in English here and
        # translated in the client - see web/src/pt.ts.
        return "melhoria", {"texto": "Mystique improved by learning from {agent}.", "agente": nome}
    if "searched the web" in baixo:
        status = "Consulting sources"
    elif "audit" in baixo or "judge" in baixo or "attempt failed" in baixo:
        status = "Checking the answer"
    elif limpo.startswith("⚠"):
        return "erro", {"texto": limpo.removeprefix("⚠").strip()}
    else:
        status = "Thinking"
    return "status", {"texto": status}


def _serializar_absorcao(absorcao: Absorcao) -> dict:
    return {
        "agente_id": absorcao.agente_id,
        "nome": absorcao.nome,
        "perfil": absorcao.perfil,
        "poderes": [{"id": p, "descricao": PODERES[p].descricao} for p in absorcao.poderes if p in PODERES],
        "protocolo": absorcao.protocolo,
        "descartado": absorcao.descartado,
    }


def _construir_snapshot(mundo: Mundo) -> dict:
    agentes = []
    for agente_id, agente in mundo.agentes.items():
        absorcao = mundo.absorcoes.get(agente_id)
        conquistadas = set(absorcao.poderes) if absorcao else set()
        vereditos = getattr(mundo, "_ultimos_vereditos", {})
        capacidades = []
        for poder_id in poderes_de(agente_id):
            veredito = vereditos.get((agente_id, poder_id))
            if poder_id in conquistadas:
                estado = "confirmada"
            elif veredito is not None and not veredito[0]:
                estado = "rejeitada"
            elif poder_id in agente.observados:
                estado = "observada_pendente"
            else:
                estado = "nao_observada"
            capacidades.append({
                "id": poder_id,
                "estado": estado,
                "motivo": veredito[1] if estado == "rejeitada" and veredito else None,
            })
        feitos, total = mundo.progresso(agente_id)
        agentes.append({
            "id": agente_id,
            "nome": agente.nome,
            "apresentacao": agente.apresentacao,
            "externo": bool(agente.url),
            "capacidades": capacidades,
            "descartado": bool(absorcao and absorcao.descartado),
            "essencia_absorvida": bool(absorcao and absorcao.perfil),
            "progresso": {"feitos": feitos, "total": total},
        })
    absorcoes = {aid: _serializar_absorcao(a) for aid, a in mundo.absorcoes.items()}
    return {"modo": mundo.modo, "agentes": agentes, "absorcoes": absorcoes}


class InterrompivelMixin:
    """Mixed into MundoBem/MundoMal (see MundoBemServidor/MundoMalServidor below). Never used
    on its own."""

    def __init__(self, *args, eventos: BarramentoEventos, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._eventos = eventos
        self._resposta_publica = ""
        self._erro_publico = ""
        self._status_publico = ""
        saida_original = self.avisar

        def narrar(texto: str) -> None:
            saida_original(texto)
            nome, valor = _evento_publico(texto)
            if nome == "resposta":
                self._resposta_publica = valor["texto"]
            elif nome == "erro":
                self._erro_publico = valor["texto"]
            elif nome != "status" or valor["texto"] != self._status_publico:
                self._status_publico = valor["texto"] if nome == "status" else self._status_publico
                self._eventos.publicar_nowait(evento_custom(nome, valor))

        self.avisar = narrar
        self._pendentes: dict[str, "asyncio.Future[bool]"] = {}
        self._ultimos_vereditos: dict[tuple[str, str], tuple[bool, str]] = {}
        self._ja_descartados: set[str] = {
            aid for aid, absorcao in self.absorcoes.items() if absorcao.descartado
        }

    def iniciar_missao_ui(self) -> None:
        self._resposta_publica = ""
        self._erro_publico = ""
        self._status_publico = ""

    def finalizar_missao_ui(self) -> tuple[str, bool]:
        if self._resposta_publica:
            return self._resposta_publica, False
        if self._erro_publico:
            return self._erro_publico, True
        return "The mission ended without a final answer.", True

    def snapshot(self) -> dict:
        return _construir_snapshot(self)

    def assinar_eventos(self):
        return self._eventos.assinar()

    def desassinar_eventos(self, fila) -> None:
        self._eventos.desassinar(fila)

    async def _aguardar_aprovacao(
        self, agente: Agente, absorcao: Absorcao, descricao: str, evidencia: str,
        poder: Poder | None, motivo: str,
    ) -> bool:
        aprovado = poder is not None
        if not aprovado:
            poder_id = descricao or "unidentified capability"
            self._ultimos_vereditos[(agente.id, poder_id)] = (False, motivo)
            self._eventos.publicar_nowait(evento_snapshot(self.snapshot()))
        self._eventos.publicar_nowait(evento_custom("decisao_automatica", {
            "agente": agente.nome,
            "aprovado": aprovado,
            "texto": (
                "Mystique approved learning from {agent}."
                if aprovado else "Mystique rejected this learning from {agent}."
            ),
        }))
        return aprovado

    def decidir(self, recibo_id: str, aprovar: bool) -> bool:
        """Resolves a pending receipt. False if the id is unknown or already resolved."""
        futuro = self._pendentes.get(recibo_id)
        if futuro is None or futuro.done():
            return False
        futuro.set_result(aprovar)
        return True

    def _salvar(self, absorcao: Absorcao) -> None:
        super()._salvar(absorcao)
        if absorcao.descartado and absorcao.agente_id not in self._ja_descartados:
            self._ja_descartados.add(absorcao.agente_id)
            self._eventos.publicar_nowait(evento_custom("agente_descartado", {"agente_id": absorcao.agente_id}))
        self._eventos.publicar_nowait(evento_snapshot(self.snapshot()))

    async def conversar(self, agente_id: str, mensagem: str) -> str:
        agente = self.agentes.get(agente_id)
        antes = set(agente.observados) if agente else set()
        resultado = await super().conversar(agente_id, mensagem)
        if agente:
            novos = sorted(agente.observados - antes)
            for capacidade_id in novos:
                self._eventos.publicar_nowait(evento_custom("capacidade_observada", {
                    "agente_id": agente_id, "capacidade_id": capacidade_id,
                }))
            if novos:
                self._eventos.publicar_nowait(evento_snapshot(self.snapshot()))
        return resultado


class MundoBemServidor(InterrompivelMixin, MundoBem):
    pass


class MundoMalServidor(InterrompivelMixin, MundoMal):
    pass
