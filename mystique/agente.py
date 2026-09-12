"""Main loop: connects Mystique to the Agent SDK and narrates what happens."""

import asyncio
import json
import os
from collections.abc import Callable

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ClaudeSDKError,
    ResultMessage,
    SdkMcpTool,
    TextBlock,
    ThinkingBlock,
)

from . import agente_local
from .ferramentas import criar_servidor, ferramentas_base, nomes_permitidos
from .mundo import Mundo
from .persona import BASE

MODELO = os.getenv("MYSTIQUE_MODEL", "claude-opus-5")
_EMOJI = {"good": "🦸", "evil": "🦹"}

FerramentasExtras = Callable[[Mundo], list[SdkMcpTool]]


def montar_opcoes(mundo: Mundo, orcamento: float, persona: str, extras: FerramentasExtras) -> ClaudeAgentOptions:
    ferramentas = ferramentas_base(mundo) + extras(mundo)
    return ClaudeAgentOptions(
        system_prompt=f"{BASE}\n\n{persona}",
        model=MODELO,
        # She is born with metamorphosis only: no built-in tools, just the world's server.
        tools=[],
        mcp_servers={"mundo": criar_servidor(ferramentas)},
        allowed_tools=nomes_permitidos(ferramentas),
        permission_mode="dontAsk",
        cwd=str(mundo.pasta.parent),
        max_budget_usd=orcamento,
        effort="high",
        thinking={"type": "adaptive", "display": "summarized"},
        # Does not inherit settings/hooks/CLAUDE.md from the machine: reproducible behavior.
        setting_sources=[],
    )


class Narrador:
    """Prints the SDK stream. Contacts and conquests are narrated by the Mundo itself."""

    def __init__(self, mundo: Mundo, verbose: bool) -> None:
        self.mundo = mundo
        self.verbose = verbose

    def mensagem(self, msg: object) -> None:
        if isinstance(msg, AssistantMessage):
            for bloco in msg.content:
                if isinstance(bloco, TextBlock):
                    print(f"\n[{self.mundo.nome_atual}] {bloco.text}")
                elif self.verbose and isinstance(bloco, ThinkingBlock) and bloco.thinking:
                    print(f"   💭 {bloco.thinking}")
        elif isinstance(msg, ResultMessage):
            custo = f"${msg.total_cost_usd:.4f}" if msg.total_cost_usd is not None else "?"
            print(f"\n— {msg.subtype} · total cost {custo}")


async def executar(
    missao: str | None, mundo: Mundo, orcamento: float, verbose: bool, persona: str,
    extras: FerramentasExtras, openai_config: dict[str, str] | None = None,
    historico: list[dict] | None = None,
) -> None:
    """With a mission: runs once and exits. Without one: interactive mode with session memory."""
    if openai_config or agente_local.ativo():  # self-hosted Mystique: see mystique/agente_local.py
        await agente_local.executar(
            missao, mundo, orcamento, verbose, persona, extras, openai_config=openai_config,
            historico=historico,
        )
        return

    narrador = Narrador(mundo, verbose)
    conquistas = sum(len(a.poderes) for a in mundo.absorcoes.values())
    print(
        f"{_EMOJI.get(mundo.modo, '🦎')} Mystique ({mundo.modo}) · model {MODELO} · "
        f"{len(mundo.agentes)} agents · {conquistas} abilities in memory · budget ${orcamento:.2f}"
    )

    async with ClaudeSDKClient(options=montar_opcoes(mundo, orcamento, persona, extras)) as client:
        pedido = missao
        while True:
            if pedido is None:
                try:
                    pedido = (await asyncio.to_thread(input, f"\n[{mundo.nome_atual}]> ")).strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if pedido.lower() in {"exit", "quit", "sair"}:
                    break
                if not pedido:
                    pedido = None
                    continue
            try:
                if historico:
                    transcricao = json.dumps(historico[-40:], ensure_ascii=False)
                    pedido = (
                        "<conversation_history>Earlier turns in this same user-selected session: "
                        f"{transcricao}</conversation_history>\n\n{pedido}"
                    )
                    historico = None
                await client.query(mundo.envelopar(pedido))
                async for msg in client.receive_response():
                    narrador.mensagem(msg)
            except ClaudeSDKError as erro:
                print(f"\n⚠ mission interrupted: {erro}")
            if missao is not None:
                break
            pedido = None
