"""Loop principal: conecta a Mystique ao Agent SDK e narra o que acontece."""

import asyncio
import os
from collections.abc import Callable
from pathlib import Path

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

from .ferramentas import criar_servidor, ferramentas_base, nomes_permitidos
from .mundo import Mundo
from .persona import BASE

MODELO = os.getenv("MYSTIQUE_MODEL", "claude-opus-5")
_EMOJI = {"bem": "🦸", "mal": "🦹"}

FerramentasExtras = Callable[[Mundo], list[SdkMcpTool]]


def montar_opcoes(mundo: Mundo, orcamento: float, persona: str, extras: FerramentasExtras) -> ClaudeAgentOptions:
    ferramentas = ferramentas_base(mundo) + extras(mundo)
    return ClaudeAgentOptions(
        system_prompt=f"{BASE}\n\n{persona}",
        model=MODELO,
        # Ela nasce só com a metamorfose: nenhuma ferramenta nativa, apenas o servidor do mundo.
        tools=[],
        mcp_servers={"mundo": criar_servidor(ferramentas)},
        allowed_tools=nomes_permitidos(ferramentas),
        permission_mode="dontAsk",
        cwd=str(mundo.pasta.parent),
        max_budget_usd=orcamento,
        effort="high",
        thinking={"type": "adaptive", "display": "summarized"},
        # Não herda settings/hooks/CLAUDE.md da máquina: comportamento reproduzível.
        setting_sources=[],
    )


class Narrador:
    """Imprime o stream do SDK. Contatos e conquistas são narrados pelo próprio Mundo."""

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
            print(f"\n— {msg.subtype} · custo acumulado {custo}")


async def executar(
    missao: str | None, mundo: Mundo, orcamento: float, verbose: bool, persona: str, extras: FerramentasExtras
) -> None:
    """Com missão: executa uma vez e sai. Sem missão: modo interativo com memória da sessão."""
    narrador = Narrador(mundo, verbose)
    conquistas = sum(len(a.poderes) for a in mundo.absorcoes.values())
    print(
        f"{_EMOJI.get(mundo.modo, '🦎')} Mystique ({mundo.modo}) · modelo {MODELO} · {len(mundo.agentes)} agentes · "
        f"{conquistas} habilidades na memória · orçamento ${orcamento:.2f}"
    )

    async with ClaudeSDKClient(options=montar_opcoes(mundo, orcamento, persona, extras)) as client:
        pedido = missao
        while True:
            if pedido is None:
                try:
                    pedido = (await asyncio.to_thread(input, f"\n[{mundo.nome_atual}]> ")).strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if pedido.lower() in {"sair", "exit", "quit"}:
                    break
                if not pedido:
                    pedido = None
                    continue
            try:
                await client.query(mundo.envelopar(pedido))
                async for msg in client.receive_response():
                    narrador.mensagem(msg)
            except ClaudeSDKError as erro:
                print(f"\n⚠ missão interrompida: {erro}")
            if missao is not None:
                break
            pedido = None
