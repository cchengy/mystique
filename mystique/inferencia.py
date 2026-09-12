"""OpenAI-compatible backend for the world side (agents, judge, consent).

Why this exists
---------------
Every world-side inference goes through ``Mundo._chamar``. Pointing it at a
self-hosted model removes the demo's dependency on event wifi and API quota.

Mystique herself is NOT affected: she runs on the Claude Agent SDK because she
needs its MCP tool loop, and the Claude CLI rejects a non-Claude model id
outright. Only the world moves.

Measured on the target box (llama-server, Qwen3.8-27B-UD-Q6_K, --jinja on):
tool calling and json_schema both work, and the judge's real schema is answered
correctly. Pointing ``anthropic.AsyncAnthropic`` at it does NOT work - that
server has no Anthropic route - which is why this translates instead.

The adapter returns **Anthropic-shaped** objects, so ``conversar`` and ``_json``
need no changes at all, and ``tests/test_offline.py`` keeps working: it already
fakes exactly this shape.

Three findings from testing the box, all handled below:
  * it is a reasoning model - a small max_tokens returns EMPTY content, so never
    shrink max_tokens for this backend;
  * ``reasoning_content`` is a separate field, so the thinking never pollutes the
    character's text and is deliberately dropped here;
  * there is no "refusal" finish reason to map.
"""

import json
import os
from types import SimpleNamespace as NS

import anthropic

PROVEDOR = os.getenv("MYSTIQUE_WORLD_PROVIDER", "anthropic").strip().lower()
BASE_URL = os.getenv("MYSTIQUE_WORLD_BASE_URL", "").rstrip("/")
MODELO = os.getenv("MYSTIQUE_WORLD_MODEL", "")
CHAVE = os.getenv("MYSTIQUE_WORLD_API_KEY", "not-used")  # ASCII only: it goes in a header
# Reasoning effort, when the server takes it (DeepSeek does: low/medium/high/xhigh).
# Default to "low" rather than nothing: measured on deepseek-flash, a trivial reply
# spends ~78% of its output tokens on reasoning when no effort is sent, and those
# tokens are the wait. Sending "low" cut a single call from 2.45s to 1.98s and the
# reasoning from 199 to 155 tokens. Set MYSTIQUE_EFFORT to override.
ESFORCO = os.getenv("MYSTIQUE_EFFORT", "low").strip()


def ativo() -> bool:
    """True when the world should talk to an OpenAI-compatible server."""
    return PROVEDOR == "openai" and bool(BASE_URL and MODELO)


def descricao() -> str:
    return f"{MODELO} @ {BASE_URL}"


# --- Anthropic -> OpenAI ------------------------------------------------------

def _mensagens(system: str | None, mensagens: list[dict]) -> list[dict]:
    """Flatten Anthropic history (with tool_use / tool_result blocks) into OpenAI turns."""
    saida: list[dict] = []
    if system:
        saida.append({"role": "system", "content": system})
    for msg in mensagens:
        conteudo = msg["content"]
        if isinstance(conteudo, str):
            saida.append({"role": msg["role"], "content": conteudo})
            continue
        # A list of blocks: either an assistant turn with tool_use, or tool results.
        textos, chamadas, resultados = [], [], []
        for bloco in conteudo:
            tipo = bloco.get("type") if isinstance(bloco, dict) else bloco.type
            get = bloco.get if isinstance(bloco, dict) else (lambda k, _b=bloco: getattr(_b, k, None))
            if tipo == "text":
                textos.append(get("text") or "")
            elif tipo == "tool_use":
                chamadas.append({
                    "id": get("id"),
                    "type": "function",
                    "function": {"name": get("name"), "arguments": json.dumps(get("input") or {}, ensure_ascii=False)},
                })
            elif tipo == "tool_result":
                resultados.append({
                    "role": "tool",
                    "tool_call_id": get("tool_use_id"),
                    "content": str(get("content") or ""),
                })
        if chamadas or (textos and msg["role"] == "assistant"):
            turno: dict = {"role": "assistant", "content": "".join(textos) or None}
            if chamadas:
                turno["tool_calls"] = chamadas
            saida.append(turno)
        saida.extend(resultados)
    return saida


def _ferramentas(tools: list[dict]) -> list[dict]:
    return [
        {"type": "function", "function": {
            "name": f["name"], "description": f.get("description", ""), "parameters": f["input_schema"]}}
        for f in tools
    ]


def _escolha(tool_choice: dict | None):
    if not tool_choice:
        return None
    return "none" if tool_choice.get("type") == "none" else "auto"


def _formato(output_config: dict | None):
    fmt = (output_config or {}).get("format")
    if not fmt or fmt.get("type") != "json_schema":
        return None
    return {"type": "json_schema",
            "json_schema": {"name": "resposta", "strict": True, "schema": fmt["schema"]}}


# --- OpenAI -> Anthropic ------------------------------------------------------

def _com_esquema(mensagens: list[dict], esquema: dict) -> list[dict]:
    """Plain JSON mode has no schema, so state it in the system turn instead."""
    instrucao = "Reply ONLY with JSON matching this schema: " + json.dumps(esquema, ensure_ascii=False)
    saida = [dict(m) for m in mensagens]
    for m in saida:
        if m.get("role") == "system":
            m["content"] = f"{m.get('content') or ''}\n\n{instrucao}".strip()
            return saida
    return [{"role": "system", "content": instrucao}, *saida]


def _resposta(bruto: dict):
    escolha = bruto["choices"][0]
    msg = escolha.get("message") or {}
    blocos = []
    texto = msg.get("content") or ""      # reasoning_content is dropped on purpose
    if texto:
        blocos.append(NS(type="text", text=texto))
    for i, chamada in enumerate(msg.get("tool_calls") or []):
        fn = chamada.get("function") or {}
        try:
            argumentos = json.loads(fn.get("arguments") or "{}")
        except json.JSONDecodeError:
            argumentos = {}
        blocos.append(NS(type="tool_use", id=chamada.get("id") or f"call_{i}",
                         name=fn.get("name"), input=argumentos))
    # No "refusal" exists here: tool_calls -> tool_use, everything else -> end_turn.
    parada = "tool_use" if escolha.get("finish_reason") == "tool_calls" else "end_turn"
    return NS(content=blocos, stop_reason=parada)


class ClienteOpenAI:
    """Minimal async client with the same call shape Mundo._chamar already uses."""

    # Not every OpenAI-compatible server takes json_schema. DeepSeek, for one, answers
    # "This response_format type is unavailable now" and only does plain JSON mode. We
    # try the strict form once, then fall back and remember, so it costs one call ever.
    _json_schema_ok = True

    def __init__(self, base_url: str, modelo: str, chave: str, timeout: float = 60.0):
        # httpx2 is what the anthropic package already depends on, so this adds
        # no new requirement. httpx is accepted as a fallback for other setups.
        try:
            import httpx2 as httpx
        except ImportError:  # pragma: no cover
            import httpx

        self._modelo = modelo
        self._http = httpx.AsyncClient(
            base_url=base_url, timeout=timeout,
            headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"},
        )

    async def chamar(self, *, system=None, messages, max_tokens=4000,
                     output_config=None, tools=None, tool_choice=None, **_ignorado):
        corpo: dict = {
            "model": self._modelo,
            "messages": _mensagens(system, messages),
            # Never shrink this: it is a reasoning model and a small budget returns
            # empty content, which reads as a bug on screen.
            "max_tokens": max_tokens,
        }
        if tools:
            corpo["tools"] = _ferramentas(tools)
            escolha = _escolha(tool_choice)
            if escolha:
                corpo["tool_choice"] = escolha
        if ESFORCO:
            corpo["reasoning_effort"] = ESFORCO

        formato = _formato(output_config)
        esquema = ((output_config or {}).get("format") or {}).get("schema")
        if formato and type(self)._json_schema_ok:
            corpo["response_format"] = formato
        elif esquema:
            corpo["response_format"] = {"type": "json_object"}
            corpo["messages"] = _com_esquema(corpo["messages"], esquema)

        try:
            r = await self._http.post("/chat/completions", json=corpo)
            if r.status_code == 400 and formato and type(self)._json_schema_ok and "response_format" in r.text:
                # This server does not do json_schema. Degrade once, for good.
                type(self)._json_schema_ok = False
                corpo["response_format"] = {"type": "json_object"}
                corpo["messages"] = _com_esquema(corpo["messages"], esquema)
                r = await self._http.post("/chat/completions", json=corpo)
            r.raise_for_status()
            return _resposta(r.json())
        except Exception as erro:
            # Mundo already handles anthropic.APIError everywhere; reuse it so the
            # engine's existing error paths work unchanged for both backends.
            raise anthropic.APIConnectionError(request=None) from erro
