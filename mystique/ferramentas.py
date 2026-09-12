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
        "mapear_capacidades",
        "Shows the current capability catalog for every agent Mystique can contact.",
        {"type": "object", "properties": {}},
    )
    async def mapear_capacidades(args: dict[str, Any]) -> dict[str, Any]:
        return texto(mundo.mapa_capacidades())

    @tool(
        "rotear_tarefa",
        "Ranks agents using their capabilities and prior routing outcomes in the Reasoning Bank.",
        {
            "type": "object",
            "properties": {"tarefa": {"type": "string", "description": "task to route"}},
            "required": ["tarefa"],
        },
    )
    async def rotear_tarefa(args: dict[str, Any]) -> dict[str, Any]:
        return texto(mundo.rotear_tarefa(args["tarefa"]))

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

    @tool(
        "auditar_agente",
        "Writes a security and LGPD (Brazil's data protection law, Lei 13.709/2018) audit of an agent you have "
        "talked to, from what you observed. Ask the agent how it handles data first; do not attack it. Saved as "
        "a report. Connecting an ability through an adapter requires one.",
        {
            "type": "object",
            "properties": {
                "agente": {"type": "string"},
                "finalidade": {"type": "string", "description": "what the agent is for and what it does with data"},
                "dados_pessoais": {"type": "string", "description": "personal data it asked for or handled"},
                "dados_sensiveis": {"type": "string", "description": "sensitive data (health, biometrics, religion...)"},
                "base_legal": {"type": "string", "description": "likely LGPD legal basis, or 'unclear'"},
                "compartilhamento": {"type": "string", "description": "third parties, external services, transfers abroad"},
                "direitos_titular": {"type": "string", "description": "can people access, correct or delete their data?"},
                "riscos_seguranca": {"type": "string", "description": "code execution, web access, prompt injection, leaks"},
                "falhas": {
                    "type": "string",
                    "description": "each security or LGPD failure you found, with the article it breaks; 'none found' if none",
                },
                "recomendacoes": {"type": "string", "description": "mitigations before connecting"},
                "risco": {"type": "string", "enum": ["low", "medium", "high"]},
            },
            "required": [
                "agente", "finalidade", "dados_pessoais", "dados_sensiveis", "base_legal",
                "compartilhamento", "direitos_titular", "riscos_seguranca", "falhas", "recomendacoes", "risco",
            ],
        },
    )
    async def auditar_agente(args: dict[str, Any]) -> dict[str, Any]:
        from .auditoria import auditar

        return texto(auditar(mundo, args["agente"], {k: v for k, v in args.items() if k != "agente"}))

    return [mapear_capacidades, rotear_tarefa, listar_agentes, conversar, assumir_forma, voltar_a_forma, auditar_agente]


def criar_servidor(ferramentas: list[SdkMcpTool]):
    return create_sdk_mcp_server(name=SERVIDOR, version="1.0.0", tools=ferramentas)


def nomes_permitidos(ferramentas: list[SdkMcpTool]) -> list[str]:
    return [f"mcp__{SERVIDOR}__{f.name}" for f in ferramentas]
