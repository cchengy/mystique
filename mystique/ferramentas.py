"""Ferramentas comuns às duas versões, expostas como servidor MCP in-process.

As funções compartilham a instância de Mundo com o loop principal, então o estado
vive em Python e não na memória do modelo. Cada versão soma as próprias ferramentas
(bem/ferramentas.py, mal/ferramentas.py).
"""

from typing import Any

from claude_agent_sdk import SdkMcpTool, create_sdk_mcp_server, tool

from .mundo import FORMA_ORIGINAL, Mundo

SERVIDOR = "mundo"

_PERFIL = {
    "type": "object",
    "properties": {
        "agente": {"type": "string", "description": "id do agente contatado"},
        "personalidade": {"type": "string", "description": "traços centrais observados no contato"},
        "tom_de_voz": {"type": "string"},
        "vocabulario": {
            "type": "string",
            "description": "gírias, bordões e jeito de construir frases, com exemplos literais do contato",
        },
        "valores_e_manias": {"type": "string"},
        "como_responde": {"type": "string", "description": "tamanho, estrutura e ritmo típicos das respostas"},
    },
    "required": ["agente", "personalidade", "tom_de_voz", "vocabulario", "valores_e_manias", "como_responde"],
}


def texto(conteudo: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": conteudo}]}


def ferramentas_base(mundo: Mundo) -> list[SdkMcpTool]:
    @tool(
        "listar_agentes",
        "Lista os agentes do mundo (só a apresentação pública), seu progresso em cada um e o que você já conquistou.",
        {"type": "object", "properties": {}},
    )
    async def listar_agentes(args: dict[str, Any]) -> dict[str, Any]:
        linhas = "\n".join(mundo.descrever(a) for a in mundo.agentes.values())
        return texto(f"Agentes:\n{linhas}\n\n{mundo.resumo()}".strip())

    @tool(
        "conversar",
        "Envia uma mensagem a um agente do mundo e devolve a resposta dele. O agente lembra da conversa. "
        "Quando ele usa uma habilidade especial, você percebe e vê o resultado.",
        {
            "type": "object",
            "properties": {"agente": {"type": "string", "description": "id do agente"}, "mensagem": {"type": "string"}},
            "required": ["agente", "mensagem"],
        },
    )
    async def conversar(args: dict[str, Any]) -> dict[str, Any]:
        return texto(await mundo.conversar(args["agente"], args["mensagem"]))

    @tool(
        "assumir_forma",
        "Absorve a essência (personalidade) de um agente com quem você teve contato, a partir do perfil "
        "deduzido da conversa. Use só o que observou; não invente traços.",
        _PERFIL,
    )
    async def assumir_forma(args: dict[str, Any]) -> dict[str, Any]:
        perfil = {chave: valor for chave, valor in args.items() if chave != "agente"}
        return texto(mundo.assumir(args["agente"], perfil))

    @tool(
        "voltar_a_forma",
        f"Troca para uma essência já absorvida, sem novo contato, ou use '{FORMA_ORIGINAL}' para a forma original.",
        {"type": "object", "properties": {"agente": {"type": "string"}}, "required": ["agente"]},
    )
    async def voltar_a_forma(args: dict[str, Any]) -> dict[str, Any]:
        return texto(mundo.voltar(args["agente"]))

    return [listar_agentes, conversar, assumir_forma, voltar_a_forma]


def criar_servidor(ferramentas: list[SdkMcpTool]):
    return create_sdk_mcp_server(name=SERVIDOR, version="1.0.0", tools=ferramentas)


def nomes_permitidos(ferramentas: list[SdkMcpTool]) -> list[str]:
    return [f"mcp__{SERVIDOR}__{f.name}" for f in ferramentas]
