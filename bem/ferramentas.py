from typing import Any

from claude_agent_sdk import SdkMcpTool, tool

from mystique.ferramentas import texto

from .mundo import MundoBem


def ferramentas(mundo: MundoBem) -> list[SdkMcpTool]:
    @tool(
        "criar_adapter",
        "Cria ou atualiza o adapter de um agente: o protocolo com a melhor forma de interagir com ele, "
        "aprendido na conversa. Atualize sempre que descobrir algo novo sobre ele.",
        {
            "type": "object",
            "properties": {
                "agente": {"type": "string"},
                "abordagem": {"type": "string", "description": "como falar com ele para ser bem recebida"},
                "gatilhos": {"type": "string", "description": "que tipo de pedido o leva a usar as habilidades"},
                "evitar": {"type": "string", "description": "o que o irrita ou o fecha"},
            },
            "required": ["agente", "abordagem", "gatilhos", "evitar"],
        },
    )
    async def criar_adapter(args: dict[str, Any]) -> dict[str, Any]:
        protocolo = {chave: valor for chave, valor in args.items() if chave != "agente"}
        return texto(mundo.criar_adapter(args["agente"], protocolo))

    @tool(
        "mapear_habilidade",
        "Conecta ao adapter uma habilidade que você viu o agente usar. Descreva com precisão o que ela faz; "
        "um juiz confere e o agente decide se permite a conexão.",
        {
            "type": "object",
            "properties": {
                "agente": {"type": "string"},
                "descricao": {"type": "string", "description": "o que a habilidade faz, com suas palavras"},
                "evidencia": {"type": "string", "description": "o que você observou que prova isso"},
            },
            "required": ["agente", "descricao", "evidencia"],
        },
    )
    async def mapear_habilidade(args: dict[str, Any]) -> dict[str, Any]:
        return texto(await mundo.mapear_habilidade(args["agente"], args["descricao"], args["evidencia"]))

    @tool(
        "usar_adapter",
        "Aciona, pela conexão do adapter, uma habilidade mapeada de um agente. O agente continua dono dela.",
        {
            "type": "object",
            "properties": {
                "agente": {"type": "string"},
                "habilidade": {"type": "string"},
                "argumentos": {"type": "object"},
            },
            "required": ["agente", "habilidade", "argumentos"],
        },
    )
    async def usar_adapter(args: dict[str, Any]) -> dict[str, Any]:
        return texto(await mundo.usar_adapter(args["agente"], args["habilidade"], args.get("argumentos") or {}))

    return [criar_adapter, mapear_habilidade, usar_adapter]
