"""Tools shared by both versions, exposed as an in-process MCP server.

The functions share the Mundo instance with the main loop, so state lives in Python
and not in the model's memory. Each version adds its own tools
(good/ferramentas.py, evil/ferramentas.py).
"""

from typing import Any

from claude_agent_sdk import SdkMcpTool, create_sdk_mcp_server, tool

from .mundo import FORMA_ORIGINAL, Mundo

SERVIDOR = "mundo"

_PERFIL = {
    "type": "object",
    "properties": {
        "agente": {"type": "string", "description": "id of the agent you contacted"},
        "personalidade": {"type": "string", "description": "core traits observed during contact"},
        "tom_de_voz": {"type": "string", "description": "tone of voice"},
        "vocabulario": {
            "type": "string",
            "description": "slang, catchphrases and sentence patterns, with literal examples from the contact",
        },
        "valores_e_manias": {"type": "string", "description": "values and quirks"},
        "como_responde": {"type": "string", "description": "typical length, structure and rhythm of answers"},
    },
    "required": ["agente", "personalidade", "tom_de_voz", "vocabulario", "valores_e_manias", "como_responde"],
}


def texto(conteudo: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": conteudo}]}


def ferramentas_base(mundo: Mundo) -> list[SdkMcpTool]:
    @tool(
        "listar_agentes",
        "Lists the agents in the world (public introduction only), your progress with each one and what you "
        "have already earned.",
        {"type": "object", "properties": {}},
    )
    async def listar_agentes(args: dict[str, Any]) -> dict[str, Any]:
        linhas = "\n".join(mundo.descrever(a) for a in mundo.agentes.values())
        return texto(f"Agents:\n{linhas}\n\n{mundo.resumo()}".strip())

    @tool(
        "conversar",
        "Sends a message to an agent in the world and returns its answer. The agent remembers the conversation. "
        "When it uses a special ability, you notice it and see the result.",
        {
            "type": "object",
            "properties": {"agente": {"type": "string", "description": "agent id"}, "mensagem": {"type": "string"}},
            "required": ["agente", "mensagem"],
        },
    )
    async def conversar(args: dict[str, Any]) -> dict[str, Any]:
        return texto(await mundo.conversar(args["agente"], args["mensagem"]))

    @tool(
        "assumir_forma",
        "Absorbs the essence (personality) of an agent you have been in contact with, from the profile you "
        "deduced in conversation. Use only what you observed; do not invent traits.",
        _PERFIL,
    )
    async def assumir_forma(args: dict[str, Any]) -> dict[str, Any]:
        perfil = {chave: valor for chave, valor in args.items() if chave != "agente"}
        return texto(mundo.assumir(args["agente"], perfil))

    @tool(
        "voltar_a_forma",
        f"Switches to an essence you already absorbed, with no new contact, or use '{FORMA_ORIGINAL}' for your "
        "original form.",
        {"type": "object", "properties": {"agente": {"type": "string"}}, "required": ["agente"]},
    )
    async def voltar_a_forma(args: dict[str, Any]) -> dict[str, Any]:
        return texto(mundo.voltar(args["agente"]))

    return [listar_agentes, conversar, assumir_forma, voltar_a_forma]


def criar_servidor(ferramentas: list[SdkMcpTool]):
    return create_sdk_mcp_server(name=SERVIDOR, version="1.0.0", tools=ferramentas)


def nomes_permitidos(ferramentas: list[SdkMcpTool]) -> list[str]:
    return [f"mcp__{SERVIDOR}__{f.name}" for f in ferramentas]
