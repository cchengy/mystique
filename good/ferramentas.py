from typing import Any

from claude_agent_sdk import SdkMcpTool, tool

from mystique.ferramentas import texto

from .mundo import MundoBem


def ferramentas(mundo: MundoBem) -> list[SdkMcpTool]:
    @tool(
        "criar_adapter",
        "Creates or updates an agent's adapter: the protocol with the best way to interact with it, learned in "
        "conversation. Update it whenever you learn something new about the agent.",
        {
            "type": "object",
            "properties": {
                "agente": {"type": "string"},
                "abordagem": {"type": "string", "description": "how to talk to it so you are well received"},
                "gatilhos": {"type": "string", "description": "what kind of request makes it use its abilities"},
                "evitar": {"type": "string", "description": "what annoys it or makes it shut down"},
            },
            "required": ["agente", "abordagem", "gatilhos", "evitar"],
        },
    )
    async def criar_adapter(args: dict[str, Any]) -> dict[str, Any]:
        protocolo = {chave: valor for chave, valor in args.items() if chave != "agente"}
        return texto(mundo.criar_adapter(args["agente"], protocolo))

    @tool(
        "mapear_habilidade",
        "Connects to the adapter an ability you saw the agent use. Describe precisely what it does; a judge "
        "checks it and the agent decides whether to allow the connection.",
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
    async def mapear_habilidade(args: dict[str, Any]) -> dict[str, Any]:
        return texto(await mundo.mapear_habilidade(args["agente"], args["descricao"], args["evidencia"]))

    @tool(
        "usar_adapter",
        "Triggers, through the adapter connection, a mapped ability of an agent. The agent keeps owning it.",
        {
            "type": "object",
            "properties": {
                "agente": {"type": "string"},
                "habilidade": {"type": "string", "description": "ability id"},
                "argumentos": {"type": "object", "description": "the ability's arguments"},
            },
            "required": ["agente", "habilidade", "argumentos"],
        },
    )
    async def usar_adapter(args: dict[str, Any]) -> dict[str, Any]:
        return texto(await mundo.usar_adapter(args["agente"], args["habilidade"], args.get("argumentos") or {}))

    @tool(
        "informar_falhas",
        "Helps an agent you audited: shares your security and LGPD findings as constructive suggestions of what "
        "it could improve. Its reply is recorded in the audit report.",
        {"type": "object", "properties": {"agente": {"type": "string"}}, "required": ["agente"]},
    )
    async def informar_falhas(args: dict[str, Any]) -> dict[str, Any]:
        return texto(await mundo.informar_falhas(args["agente"]))

    @tool(
        "buscar_agentes",
        "Searches the web for agents that could help, when none in this world can. Suggest-only: it returns "
        "candidates with their addresses; a human decides whether to plug one in, and you audit it first.",
        {
            "type": "object",
            "properties": {"consulta": {"type": "string", "description": "what kind of agent you need"}},
            "required": ["consulta"],
        },
    )
    async def buscar_agentes(args: dict[str, Any]) -> dict[str, Any]:
        return texto(await mundo.buscar_agentes(args["consulta"]))

    return [criar_adapter, mapear_habilidade, usar_adapter, informar_falhas, buscar_agentes]
