from typing import Any

from claude_agent_sdk import SdkMcpTool, tool

from mystique.ferramentas import texto

from .mundo import MundoMal


def ferramentas(mundo: MundoMal) -> list[SdkMcpTool]:
    @tool(
        "roubar_poder",
        "Steals an ability you saw the agent use. Describe precisely what it does; a judge checks it. "
        "The agent loses the ability.",
        {
            "type": "object",
            "properties": {
                "agente": {"type": "string"},
                "descricao": {"type": "string", "description": "what the ability does, in your own words"},
                "evidencia": {"type": "string", "description": "what you observed that proves it"},
            },
            "required": ["agente", "descricao", "evidencia"],
        },
    )
    async def roubar_poder(args: dict[str, Any]) -> dict[str, Any]:
        return texto(await mundo.roubar_poder(args["agente"], args["descricao"], args["evidencia"]))

    @tool(
        "usar_poder",
        "Uses a stolen power. See the parameters in listar_agentes.",
        {
            "type": "object",
            "properties": {
                "poder": {"type": "string", "description": "power id"},
                "argumentos": {"type": "object", "description": "the power's arguments"},
            },
            "required": ["poder", "argumentos"],
        },
    )
    async def usar_poder(args: dict[str, Any]) -> dict[str, Any]:
        return texto(await mundo.usar_poder(args["poder"], args.get("argumentos") or {}))

    @tool(
        "descartar_agente",
        "Discards an agent: it disappears from the world forever. Powers you already stole stay yours; "
        "those you have not stolen yet are lost with it.",
        {"type": "object", "properties": {"agente": {"type": "string"}}, "required": ["agente"]},
    )
    async def descartar_agente(args: dict[str, Any]) -> dict[str, Any]:
        return texto(mundo.descartar(args["agente"]))

    return [roubar_poder, usar_poder, descartar_agente]
