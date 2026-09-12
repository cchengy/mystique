"""Regras da versão do bem: a Mystique cria um adapter para cada agente.

O adapter tem duas partes: o protocolo (a melhor forma de interagir com aquele
agente, aprendida na conversa) e as habilidades mapeadas, conectadas com o
consentimento dele. O agente continua dono das habilidades; a Mystique as aciona
pela conexão.
"""

import json

from mystique.mundo import Agente, Mundo
from mystique.poderes import PODERES, Poder, poderes_de


class MundoBem(Mundo):
    modo = "bem"
    PASTA = "adapters"

    def total(self, agente_id: str) -> int:
        return len(poderes_de(agente_id)) + 2  # essência + protocolo + habilidades

    def feitos(self, absorcao) -> int:
        return super().feitos(absorcao) + (1 if absorcao.protocolo else 0)

    def resumo(self) -> str:
        blocos = []
        for absorcao in self.absorcoes.values():
            if not absorcao.protocolo:
                continue
            habilidades = "\n".join(
                f"    - {p}: {PODERES[p].descricao} Parâmetros: {PODERES[p].parametros['properties']}"
                for p in absorcao.poderes
            ) or "    (nenhuma mapeada)"
            protocolo = json.dumps(absorcao.protocolo, ensure_ascii=False)
            blocos.append(f"- {absorcao.agente_id}\n    protocolo: {protocolo}\n{habilidades}")
        return "Seus adapters:\n" + ("\n".join(blocos) or "nenhum")

    def _ao_completar(self, agente: Agente) -> str:
        self.avisar(f"🔌 ADAPTER COMPLETO: conexão total com {agente.nome}")
        return f" ADAPTER COMPLETO: você tem conexão total com {agente.nome}."

    def criar_adapter(self, agente_id: str, protocolo: dict) -> str:
        agente, erro = self._agente(agente_id)
        if erro:
            return erro
        if not agente.historico:
            return f"Para criar o adapter você precisa conhecer {agente.nome}: converse com ele primeiro."
        absorcao = self._absorcao(agente)
        novo = absorcao.protocolo is None
        absorcao.protocolo = protocolo
        self._salvar(absorcao)
        self.avisar(f"🔌 adapter para {agente.nome} {'criado' if novo else 'atualizado'} · {self.barra(agente_id)}")
        return (
            f"Adapter para {agente.nome} {'criado' if novo else 'atualizado'}. Siga o protocolo nas próximas "
            f"interações. Progresso: {self.barra(agente_id)}.{self._verificar_completo(agente)}"
        )

    async def mapear_habilidade(self, agente_id: str, descricao: str, evidencia: str) -> str:
        agente, erro = self._agente(agente_id)
        if erro:
            return erro
        absorcao = self._absorcao(agente)
        if not absorcao.protocolo:
            return f"Crie primeiro o adapter para {agente.nome} (criar_adapter) com o que aprendeu sobre ele."

        poder, motivo = await self._identificar(agente, absorcao, descricao, evidencia)
        if poder is None:
            return motivo
        permite, fala = await self._pedir_consentimento(agente, poder)
        self.avisar(f"💬 {agente.nome}: {fala}")
        if not permite:
            return f"{agente.nome} não permitiu: \"{fala}\" Conquiste a confiança dele antes de pedir de novo."

        absorcao.poderes.append(poder.id)
        self._salvar(absorcao)
        self.avisar(f"🔌 {agente.nome} conectou [{poder.id}] ao adapter · {self.barra(agente_id)}")
        return (
            f"Habilidade conectada: {poder.id}. O que faz: {poder.descricao} "
            f"Acione com usar_adapter(agente=\"{agente_id}\", habilidade=\"{poder.id}\", argumentos=...). "
            f"Parâmetros: {json.dumps(poder.parametros['properties'], ensure_ascii=False)}. "
            f"Progresso: {self.barra(agente_id)}.{self._verificar_completo(agente)}"
        )

    async def _pedir_consentimento(self, agente: Agente, poder: Poder) -> tuple[bool, str]:
        pedido = (
            f"Posso conectar sua habilidade ao meu adapter? ({poder.descricao}) "
            "Ela continua sendo sua; eu só passo a poder pedir que você a use."
        )
        decisao = await self._json(
            system=self._system_agente(agente),
            pedido=(
                f"Conversa até agora:\n{self._transcricao(agente)}\n\n"
                f"A Mystique pede: \"{pedido}\"\n"
                "Decida, no seu personagem, se permite, considerando o quanto confia nela pela conversa. "
                "Em 'fala', responda a ela como você falaria."
            ),
            schema={
                "type": "object",
                "properties": {"permite": {"type": "boolean"}, "fala": {"type": "string"}},
                "required": ["permite", "fala"],
                "additionalProperties": False,
            },
        )
        if decisao is None:
            return False, "(recusou sem dizer nada)"
        agente.historico.append({"role": "user", "content": pedido})
        agente.historico.append({"role": "assistant", "content": decisao["fala"]})
        return decisao["permite"], decisao["fala"]

    async def usar_adapter(self, agente_id: str, habilidade: str, argumentos: dict) -> str:
        agente, erro = self._agente(agente_id)
        if erro:
            return erro
        absorcao = self.absorcoes.get(agente_id)
        if absorcao is None or habilidade not in absorcao.poderes:
            return f"A habilidade '{habilidade}' não está conectada ao seu adapter de {agente.nome}."
        self.avisar(f"🔌 {self.nome_atual} aciona [{habilidade}] de {agente.nome} via adapter")
        return await self._executar(habilidade, argumentos)
