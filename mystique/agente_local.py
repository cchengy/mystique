"""Provider-agnostic main loop: runs Mystique herself on any OpenAI-compatible server.

Why this exists
---------------
The Claude Agent SDK path in agente.py needs a Claude model id - the CLI rejects
anything else before it even infers - so it cannot host Mystique on a self-hosted
model. This module reimplements the loop she needs, minus the SDK:

  * the world's tools, exposed as plain function definitions instead of MCP;
  * the tool loop itself;
  * the same narration.

The tools are the SAME objects agente.py uses (``SdkMcpTool`` carries ``.name``,
``.description``, ``.input_schema`` and an async ``.handler``), so both paths run
identical game logic and there is no second copy of the rules to keep in sync.

With this, the whole project - world AND Mystique - can run on one self-hosted
server, with no dependency on any vendor's API.
"""

import asyncio
import json
import os

from . import inferencia
from .mundo import Mundo
from .persona import BASE

_MAX_PASSOS = 24  # she needs many: contact, map, conquer, repeat
_EMOJI = {"good": "🦸", "evil": "🦹"}

# Mystique's own model. Falls back to the world's setting so one env var pair is enough.
BASE_URL = os.getenv("MYSTIQUE_BASE_URL") or inferencia.BASE_URL
MODELO = os.getenv("MYSTIQUE_MODEL_ID") or inferencia.MODELO


def ativo() -> bool:
    """True when Mystique herself should run on an OpenAI-compatible server."""
    return os.getenv("MYSTIQUE_PROVIDER", "").strip().lower() == "openai" and bool(BASE_URL and MODELO)


def _definicoes(ferramentas) -> list[dict]:
    return [{"name": f.name, "description": f.description, "input_schema": f.input_schema} for f in ferramentas]


def _texto_do_resultado(resultado) -> str:
    """Handlers answer in MCP shape: {"content": [{"type": "text", "text": ...}]}."""
    if isinstance(resultado, dict):
        partes = [b.get("text", "") for b in resultado.get("content", []) if isinstance(b, dict)]
        if partes:
            return "\n".join(partes)
    return str(resultado)


async def executar(
    missao, mundo: Mundo, orcamento: float, verbose: bool, persona: str, extras,
    openai_config: dict[str, str] | None = None,
    historico: list[dict] | None = None,
) -> None:
    from .ferramentas import ferramentas_base

    ferramentas = ferramentas_base(mundo) + extras(mundo)
    por_nome = {f.name: f for f in ferramentas}
    definicoes = _definicoes(ferramentas)
    config = openai_config or {}
    base_url = config.get("base_url", BASE_URL)
    modelo = config.get("modelo", MODELO)
    chave = config.get("chave", inferencia.CHAVE)
    cliente = inferencia.ClienteOpenAI(base_url, modelo, chave, timeout=180.0)
    sistema = f"{BASE}\n\n{persona}"

    conquistas = sum(len(a.poderes) for a in mundo.absorcoes.values())
    mundo.avisar(
        f"{_EMOJI.get(mundo.modo, '🦎')} Mystique ({mundo.modo}) · {modelo} @ {base_url} · "
        f"{len(mundo.agentes)} agents · {conquistas} abilities in memory · OpenAI-compatible endpoint"
    )

    historico = list(historico or [])
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
                continue

        historico.append({"role": "user", "content": mundo.envelopar(pedido)})
        try:
            for passo in range(_MAX_PASSOS):
                resposta = await cliente.chamar(
                    system=sistema, messages=historico, tools=definicoes, max_tokens=4000
                )
                historico.append({"role": "assistant", "content": resposta.content})
                for bloco in resposta.content:
                    if bloco.type == "text" and bloco.text.strip():
                        mundo.avisar(f"[{mundo.nome_atual}] {bloco.text}")
                if resposta.stop_reason != "tool_use":
                    break
                resultados = []
                for bloco in resposta.content:
                    if bloco.type != "tool_use":
                        continue
                    ferramenta = por_nome.get(bloco.name)
                    if ferramenta is None:
                        saida = f"Unknown tool: {bloco.name}"
                    else:
                        if verbose:
                            mundo.avisar(f"🔧 {bloco.name}({json.dumps(bloco.input, ensure_ascii=False)[:120]})")
                        try:
                            saida = _texto_do_resultado(await ferramenta.handler(bloco.input))
                        except Exception as erro:  # a broken tool must not kill the session
                            saida = f"Tool failed: {erro}"
                    resultados.append(
                        {"type": "tool_result", "tool_use_id": bloco.id, "content": saida}
                    )
                historico.append({"role": "user", "content": resultados})
            else:
                mundo.avisar(f"⚠ stopped after {_MAX_PASSOS} steps without a final answer.")
        except Exception as erro:
            mundo.avisar(f"⚠ mission interrupted: {erro}")

        if missao is not None:
            break
        pedido = None
