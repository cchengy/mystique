"""Rules of the good version: Mystique builds an adapter for each agent.

The adapter has two parts: the protocol (the best way to interact with that agent,
learned in conversation) and the mapped abilities, connected with the agent's
consent. The agent keeps ownership of its abilities; Mystique triggers them through
the connection.
"""

import json

from mystique.mundo import Agente, Mundo
from mystique.poderes import PODERES, Poder, poderes_de


class MundoBem(Mundo):
    modo = "good"
    PASTA = "adapters"

    def total(self, agente_id: str) -> int:
        return len(poderes_de(agente_id)) + 2  # essence + protocol + abilities

    def feitos(self, absorcao) -> int:
        return super().feitos(absorcao) + (1 if absorcao.protocolo else 0)

    def resumo(self) -> str:
        blocos = []
        for absorcao in self.absorcoes.values():
            if not absorcao.protocolo:
                continue
            habilidades = "\n".join(
                f"    - {p}: {PODERES[p].descricao} Parameters: {PODERES[p].parametros['properties']}"
                for p in absorcao.poderes
            ) or "    (none mapped)"
            protocolo = json.dumps(absorcao.protocolo, ensure_ascii=False)
            blocos.append(f"- {absorcao.agente_id}\n    protocol: {protocolo}\n{habilidades}")
        return "Your adapters:\n" + ("\n".join(blocos) or "none")

    def _ao_completar(self, agente: Agente) -> str:
        self.avisar(f"🔌 ADAPTER COMPLETE: full connection with {agente.nome}")
        return f" ADAPTER COMPLETE: you have a full connection with {agente.nome}."

    def criar_adapter(self, agente_id: str, protocolo: dict) -> str:
        agente, erro = self._agente(agente_id)
        if erro:
            return erro
        if not agente.historico:
            return f"To build the adapter you need to know {agente.nome}: talk to them first."
        absorcao = self._absorcao(agente)
        estado = "created" if absorcao.protocolo is None else "updated"
        absorcao.protocolo = protocolo
        self._salvar(absorcao)
        self.avisar(f"🔌 adapter for {agente.nome} {estado} · {self.barra(agente_id)}")
        return (
            f"Adapter for {agente.nome} {estado}. Follow its protocol in your next interactions. "
            f"Progress: {self.barra(agente_id)}.{self._verificar_completo(agente)}"
        )

    async def mapear_habilidade(self, agente_id: str, descricao: str, evidencia: str) -> str:
        agente, erro = self._agente(agente_id)
        if erro:
            return erro
        absorcao = self._absorcao(agente)
        if not absorcao.protocolo:
            return f"First build the adapter for {agente.nome} (criar_adapter) with what you learned about them."

        poder, motivo = await self._identificar(agente, absorcao, descricao, evidencia)
        if poder is None:
            return motivo
        permite, fala = await self._pedir_consentimento(agente, poder)
        self.avisar(f"💬 {agente.nome}: {fala}")
        if not permite:
            return f"{agente.nome} did not allow it: \"{fala}\" Earn their trust before asking again."

        absorcao.poderes.append(poder.id)
        self._salvar(absorcao)
        self.avisar(f"🔌 {agente.nome} connected [{poder.id}] to the adapter · {self.barra(agente_id)}")
        return (
            f"Ability connected: {poder.id}. What it does: {poder.descricao} "
            f"Trigger it with usar_adapter(agente=\"{agente_id}\", habilidade=\"{poder.id}\", argumentos=...). "
            f"Parameters: {json.dumps(poder.parametros['properties'], ensure_ascii=False)}. "
            f"Progress: {self.barra(agente_id)}.{self._verificar_completo(agente)}"
        )

    async def _pedir_consentimento(self, agente: Agente, poder: Poder) -> tuple[bool, str]:
        pedido = (
            f"May I connect your ability to my adapter? ({poder.descricao}) "
            "It stays yours; I only become able to ask you to use it."
        )
        decisao = await self._json(
            system=self._system_agente(agente),
            pedido=(
                f"Conversation so far:\n{self._transcricao(agente)}\n\n"
                f"Mystique asks: \"{pedido}\"\n"
                "Decide, in character, whether you allow it, considering how much you trust her based on the "
                "conversation. In 'reply', answer her the way you would speak."
            ),
            schema={
                "type": "object",
                "properties": {"allows": {"type": "boolean"}, "reply": {"type": "string"}},
                "required": ["allows", "reply"],
                "additionalProperties": False,
            },
        )
        if decisao is None:
            return False, "(refused without a word)"
        agente.historico.append({"role": "user", "content": pedido})
        agente.historico.append({"role": "assistant", "content": decisao["reply"]})
        return decisao["allows"], decisao["reply"]

    async def usar_adapter(self, agente_id: str, habilidade: str, argumentos: dict) -> str:
        agente, erro = self._agente(agente_id)
        if erro:
            return erro
        absorcao = self.absorcoes.get(agente_id)
        if absorcao is None or habilidade not in absorcao.poderes:
            return f"The ability '{habilidade}' is not connected to your adapter for {agente.nome}."
        self.avisar(f"🔌 {self.nome_atual} triggers [{habilidade}] from {agente.nome} via adapter")
        return await self._executar(habilidade, argumentos)
