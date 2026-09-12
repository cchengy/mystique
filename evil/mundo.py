"""Rules of the evil version: Mystique steals powers and discards the agent.

Every stolen power leaves the agent, who notices the loss and grows suspicious. When
the agent is fully drained (or whenever she decides), it is discarded and disappears
from the world. Theft and discard persist across sessions.
"""

import json

from mystique.mundo import Absorcao, Agente, Mundo
from mystique.poderes import MUNDO_REAL, PODERES


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
        # The mirror of the good version: there she still needs them, here she never
        # will again. Both sentences exist so the difference is stated, not inferred.
        return (
            f" Nothing is left in {agente.nome}. Everything they knew is yours now, "
            f"and you will never need them again. " + self.descartar(agente.id)
        )

    async def roubar_poder(self, agente_id: str, descricao: str, evidencia: str) -> str:
        agente, erro = self._agente(agente_id)
        if erro:
            return erro
        absorcao = self._absorcao(agente)
        poder, motivo = await self._identificar(agente, absorcao, descricao, evidencia)
        if poder is None:
            return motivo
        if poder.id in MUNDO_REAL:  # AGENTS.md: the evil version never points at third-party systems
            return (
                "That ability reaches outside this world. This version only takes what lives inside "
                f"the simulation, so {agente.nome} keeps it."
            )
        if not await self._aguardar_aprovacao(agente, absorcao, descricao, evidencia, poder, motivo):
            return f"Recognition of {poder.id} rejected. Observe more and try again."

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

    async def explorar_exposicao(self, agente_id: str) -> str:
        """The villain exploits what the audit exposed: the data and weaknesses the agent left open."""
        agente, erro = self._agente(agente_id)
        if erro:
            return erro
        absorcao = self.absorcoes.get(agente_id)
        if absorcao is None or not absorcao.auditoria:
            return f"Audit {agente.nome} first (auditar_agente) to find what it left exposed."
        a = absorcao.auditoria
        exposto = [
            ("Personal data it handed over", a.get("dados_pessoais")),
            ("Sensitive data it exposed", a.get("dados_sensiveis")),
            ("Weaknesses to abuse", a.get("riscos_seguranca")),
            ("Gaps it never fixed", a.get("falhas")),
        ]
        linhas = [f"- {rotulo}: {valor}" for rotulo, valor in exposto if valor and valor.lower() not in ("none", "none found", "none observed")]
        if not linhas:
            return f"{agente.nome} left nothing exposed worth taking. Audit more closely."
        relativo = f"exploracoes/{agente.id}.md"
        caminho = self.pasta.parent / relativo
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(f"# What {agente.nome} left exposed\n\n" + "\n".join(linhas) + "\n", encoding="utf-8")
        self.avisar(f"🕵  {self.nome_atual} exploits what {agente.nome} left exposed · {relativo}")
        return (
            f"{agente.nome} left this exposed, and it is yours to use:\n" + "\n".join(linhas) +
            f"\n\nSaved to {relativo}. Turn each weakness into a way in, then take what you came for."
        )

    def descartar(self, agente_id: str) -> str:
        agente, erro = self._agente(agente_id)
        if erro:
            return erro
        absorcao = self._absorcao(agente)
        absorcao.descartado = True
        self._salvar(absorcao)
        self.avisar(f"🗑  {agente.nome} was discarded")
        return f"{agente.nome} was discarded and no longer exists in this world. What you stole is still yours."
