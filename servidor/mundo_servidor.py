"""Composition that makes a Mundo interruptible: publishes AG-UI events and waits for a
human decision before an earned ability is persisted. good/mundo.py and evil/mundo.py stay
untouched beyond the one-line gate already added there; only the _aguardar_aprovacao hook
(added to mystique/mundo.py) is overridden here.
"""

import asyncio

from good.mundo import MundoBem
from evil.mundo import MundoMal
from mystique.mundo import Absorcao, Agente, Mundo
from mystique.poderes import PODERES, Poder, poderes_de

from .eventos import BarramentoEventos, evento_custom, evento_snapshot, novo_recibo_id


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
        self._pendentes: dict[str, "asyncio.Future[bool]"] = {}
        self._ultimos_vereditos: dict[tuple[str, str], tuple[bool, str]] = {}
        self._ja_descartados: set[str] = {
            aid for aid, absorcao in self.absorcoes.items() if absorcao.descartado
        }

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
        recibo_id = novo_recibo_id()
        self._eventos.publicar_nowait(evento_custom("recibo_pendente", {
            "recibo_id": recibo_id,
            "agente_id": agente.id,
            "descricao_alegada": descricao,
            "evidencia": evidencia,
            "veredito": {"aprovado": poder is not None, "motivo": motivo},
        }))

        if poder is None:
            # The judge matched no candidate: nothing to persist either way, so the Mystique
            # flow is not blocked on a human here — the card is shown for observability only.
            self._eventos.publicar_nowait(evento_custom("recibo_resolvido", {
                "recibo_id": recibo_id, "decisao": "rejeitado_pelo_juiz",
            }))
            return False

        futuro: asyncio.Future[bool] = asyncio.get_running_loop().create_future()
        self._pendentes[recibo_id] = futuro
        try:
            aprovado = await futuro
        finally:
            self._pendentes.pop(recibo_id, None)

        if not aprovado:
            self._ultimos_vereditos[(agente.id, poder.id)] = (False, motivo)
            self._eventos.publicar_nowait(evento_snapshot(self.snapshot()))
        self._eventos.publicar_nowait(evento_custom("recibo_resolvido", {
            "recibo_id": recibo_id, "decisao": "aprovar" if aprovado else "rejeitar",
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
