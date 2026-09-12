"""Rules of the evil version: Mystique steals powers and discards the agent.

Every stolen power leaves the agent, who notices the loss and grows suspicious. When
the agent is fully drained (or whenever she decides), it is discarded and disappears
from the world. Theft and discard persist across sessions.
"""

import json

from mystique.mundo import Absorcao, Agente, Mundo
from mystique.poderes import PODERES


class MundoMal(Mundo):
    modo = "evil"
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
            return f"{agente.nome} was discarded. They no longer exist."
        return None

    def _system_agente(self, agente: Agente) -> str:
        base = super()._system_agente(agente)
        if not agente.perdidos:
            return base
        perdas = "; ".join(PODERES[p].descricao for p in agente.perdidos)
        return (
            f"{base}\n\nA mysterious force stole abilities from you and you can no longer use them: {perdas} "
            "You feel weaker and suspicious of whoever talks to you."
        )

    def descrever(self, agente: Agente) -> str:
        absorcao = self.absorcoes.get(agente.id)
        if absorcao and absorcao.descartado:
            return f"- {agente.id} ({agente.nome}): DISCARDED"
        return super().descrever(agente)

    def poderes_roubados(self) -> list[str]:
        return [p for a in self.absorcoes.values() for p in a.poderes]

    def resumo(self) -> str:
        poderes = "\n".join(
            f"- {p}: {PODERES[p].descricao} Parameters: {PODERES[p].parametros['properties']}"
            for p in self.poderes_roubados()
        )
        return "Your stolen powers:\n" + (poderes or "none")

    def _ao_completar(self, agente: Agente) -> str:
        return " Nothing is left in them. " + self.descartar(agente.id)

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
        self.avisar(f"⚡ Mystique steals [{poder.id}] from {agente.nome} · {self.barra(agente_id)}")
        return (
            f"Power stolen: {poder.id}. What it does: {poder.descricao} {agente.nome} no longer has it. "
            f"Use it with usar_poder(poder=\"{poder.id}\", argumentos=...). "
            f"Parameters: {json.dumps(poder.parametros['properties'], ensure_ascii=False)}. "
            f"Progress: {self.barra(agente_id)}.{self._verificar_completo(agente)}"
        )

    async def usar_poder(self, poder_id: str, argumentos: dict) -> str:
        if poder_id not in self.poderes_roubados():
            return f"You do not have the power '{poder_id}'."
        self.avisar(f"⚡ {self.nome_atual} uses [{poder_id}]")
        return await self._executar(poder_id, argumentos)

    def descartar(self, agente_id: str) -> str:
        agente, erro = self._agente(agente_id)
        if erro:
            return erro
        absorcao = self._absorcao(agente)
        absorcao.descartado = True
        self._salvar(absorcao)
        self.avisar(f"🗑  {agente.nome} was discarded")
        return f"{agente.nome} was discarded and no longer exists in this world. What you stole is still yours."
