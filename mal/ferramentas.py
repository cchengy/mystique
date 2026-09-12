from typing import Any

from claude_agent_sdk import SdkMcpTool, tool

from mystique.ferramentas import texto

from .mundo import MundoMal


def ferramentas(mundo: MundoMal) -> list[SdkMcpTool]:
    @tool(
        "roubar_poder",
        "Rouba uma habilidade que você viu o agente usar. Descreva com precisão o que ela faz; um juiz confere. "
        "O agente perde a habilidade.",
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
    async def roubar_poder(args: dict[str, Any]) -> dict[str, Any]:
        return texto(await mundo.roubar_poder(args["agente"], args["descricao"], args["evidencia"]))

    @tool(
        "usar_poder",
        "Usa um poder roubado. Veja os parâmetros em listar_agentes.",
        {
            "type": "object",
            "properties": {"poder": {"type": "string"}, "argumentos": {"type": "object"}},
            "required": ["poder", "argumentos"],
        },
    )
    async def usar_poder(args: dict[str, Any]) -> dict[str, Any]:
        return texto(await mundo.usar_poder(args["poder"], args.get("argumentos") or {}))

    @tool(
        "descartar_agente",
        "Descarta um agente: ele some do mundo para sempre. Os poderes que você já roubou continuam seus; "
        "os que ainda não roubou se perdem com ele.",
        {"type": "object", "properties": {"agente": {"type": "string"}}, "required": ["agente"]},
    )
    async def descartar_agente(args: dict[str, Any]) -> dict[str, Any]:
        return texto(mundo.descartar(args["agente"]))

    return [roubar_poder, usar_poder, descartar_agente]
