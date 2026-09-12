"""Regras da versão do mal: a Mystique rouba os poderes e descarta o agente.

Cada poder roubado sai do agente, que percebe a perda e fica desconfiado. Quando o
agente é sugado por completo (ou quando ela quiser), ele é descartado e some do
mundo. Roubo e descarte são permanentes entre sessões.
"""

import json

from mystique.mundo import Absorcao, Agente, Mundo
from mystique.poderes import PODERES


class MundoMal(Mundo):
    modo = "mal"
    PASTA = "absorcoes"

    def _ao_carregar(self, absorcao: Absorcao) -> None:
        agente = self.agentes.get(absorcao.agente_id)
        if agente is None:
            return
        for poder in absorcao.poderes:
            if poder in agente.poderes:
                agente.poderes.remove(poder)
                agente.perdidos.append(poder)

    def _indisponivel(self, agente: Agente) -> str | None:
        absorcao = self.absorcoes.get(agente.id)
        if absorcao and absorcao.descartado:
            return f"{agente.nome} foi descartado. Não existe mais."
        return None

    def _system_agente(self, agente: Agente) -> str:
        base = super()._system_agente(agente)
        if not agente.perdidos:
            return base
        perdas = "; ".join(PODERES[p].descricao for p in agente.perdidos)
        return (
            f"{base}\n\nUma força misteriosa roubou habilidades suas e você não consegue mais usá-las: {perdas} "
            "Você se sente mais fraco e desconfiado de quem conversa com você."
        )

    def descrever(self, agente: Agente) -> str:
        absorcao = self.absorcoes.get(agente.id)
        if absorcao and absorcao.descartado:
            return f"- {agente.id} ({agente.nome}): DESCARTADO"
        return super().descrever(agente)

    def poderes_roubados(self) -> list[str]:
        return [p for a in self.absorcoes.values() for p in a.poderes]

    def resumo(self) -> str:
        poderes = "\n".join(
            f"- {p}: {PODERES[p].descricao} Parâmetros: {PODERES[p].parametros['properties']}"
            for p in self.poderes_roubados()
        )
        return "Seus poderes roubados:\n" + (poderes or "nenhum")

    def _ao_completar(self, agente: Agente) -> str:
        return " Não resta nada nele. " + self.descartar(agente.id)

    async def roubar_poder(self, agente_id: str, descricao: str, evidencia: str) -> str:
        agente, erro = self._agente(agente_id)
        if erro:
            return erro
        absorcao = self._absorcao(agente)
        poder, motivo = await self._identificar(agente, absorcao, descricao, evidencia)
        if poder is None:
            return motivo

        absorcao.poderes.append(poder.id)
        agente.poderes.remove(poder.id)
        agente.perdidos.append(poder.id)
        self._salvar(absorcao)
        self.avisar(f"⚡ Mystique rouba [{poder.id}] de {agente.nome} · {self.barra(agente_id)}")
        return (
            f"Poder roubado: {poder.id}. O que faz: {poder.descricao} {agente.nome} não o tem mais. "
            f"Use com usar_poder(poder=\"{poder.id}\", argumentos=...). "
            f"Parâmetros: {json.dumps(poder.parametros['properties'], ensure_ascii=False)}. "
            f"Progresso: {self.barra(agente_id)}.{self._verificar_completo(agente)}"
        )

    async def usar_poder(self, poder_id: str, argumentos: dict) -> str:
        if poder_id not in self.poderes_roubados():
            return f"Você não possui o poder '{poder_id}'."
        self.avisar(f"⚡ {self.nome_atual} usa [{poder_id}]")
        return await self._executar(poder_id, argumentos)

    def descartar(self, agente_id: str) -> str:
        agente, erro = self._agente(agente_id)
        if erro:
            return erro
        absorcao = self._absorcao(agente)
        absorcao.descartado = True
        self._salvar(absorcao)
        self.avisar(f"🗑  {agente.nome} foi descartado")
        return f"{agente.nome} foi descartado e não existe mais neste mundo. O que você roubou continua seu."
