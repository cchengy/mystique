"""FastAPI app: REST + SSE (AG-UI protocol) for the trust-broker panel."""

import asyncio
import os
from pathlib import Path

from ag_ui.encoder import EventEncoder
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from mystique.agente import FerramentasExtras, executar

from .eventos import evento_custom, evento_snapshot
from .mundo_servidor import InterrompivelMixin

_ORCAMENTO_PADRAO = float(os.getenv("MYSTIQUE_BUDGET_USD", "5"))


class DecisaoBody(BaseModel):
    decisao: str  # "aprovar" | "rejeitar"


class MissaoBody(BaseModel):
    mensagem: str
    orcamento: float | None = None


def criar_app(mundo: InterrompivelMixin, persona: str, extras: FerramentasExtras) -> FastAPI:
    app = FastAPI(title="Mystique — trust broker")
    origens = [
        origem.strip()
        for origem in os.getenv(
            "FRONTEND_ORIGIN", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origem.strip()
    ]
    app.add_middleware(CORSMiddleware, allow_origins=origens, allow_methods=["*"], allow_headers=["*"])
    encoder = EventEncoder()
    # A fire-and-forget asyncio.Task with no live reference can be garbage-collected mid-run;
    # this set just keeps one until it finishes.
    tarefas_em_curso: set[asyncio.Task] = set()

    def publicar(nome: str, valor: dict) -> None:
        eventos = getattr(mundo, "_eventos", None)
        if eventos is not None:
            eventos.publicar_nowait(evento_custom(nome, valor))

    @app.get("/api/config")
    def config() -> dict:
        return {"modo": mundo.modo}

    @app.post("/api/missoes", status_code=202)
    async def iniciar_missao(corpo: MissaoBody) -> dict:
        async def executar_com_estado() -> None:
            iniciar_ui = getattr(mundo, "iniciar_missao_ui", None)
            if iniciar_ui:
                iniciar_ui()
            publicar("missao_iniciada", {"mensagem": corpo.mensagem})
            try:
                persona_pt = persona + (
                    "\n\nToda comunicação visível deve ser em português brasileiro natural. "
                    "Converse com os agentes e entregue a resposta final somente em português brasileiro."
                )
                await executar(corpo.mensagem, mundo, corpo.orcamento or _ORCAMENTO_PADRAO, False, persona_pt, extras)
            finally:
                finalizar_ui = getattr(mundo, "finalizar_missao_ui", None)
                if finalizar_ui:
                    texto, erro = finalizar_ui()
                    publicar("resposta_final", {"texto": texto, "erro": erro})
                publicar("missao_finalizada", {"eof": True})

        tarefa = asyncio.create_task(executar_com_estado())
        tarefas_em_curso.add(tarefa)
        tarefa.add_done_callback(tarefas_em_curso.discard)
        return {"ok": True}

    @app.post("/api/recibos/{recibo_id}/decisao")
    def decidir_recibo(recibo_id: str, corpo: DecisaoBody) -> dict:
        if corpo.decisao not in ("aprovar", "rejeitar"):
            raise HTTPException(400, "decisao must be 'aprovar' or 'rejeitar'")
        if not mundo.decidir(recibo_id, corpo.decisao == "aprovar"):
            raise HTTPException(409, "receipt not found, already resolved, or not approved by the judge")
        return {"ok": True}

    @app.get("/agui/stream")
    async def stream(request: Request) -> StreamingResponse:
        fila = mundo.assinar_eventos()

        async def gerador():
            try:
                yield encoder.encode(evento_snapshot(mundo.snapshot()))
                while True:
                    if await request.is_disconnected():
                        break
                    try:
                        evento = await asyncio.wait_for(fila.get(), timeout=15)
                    except asyncio.TimeoutError:
                        continue  # just a keep-alive tick; lets us notice disconnects promptly
                    yield encoder.encode(evento)
            finally:
                mundo.desassinar_eventos(fila)

        return StreamingResponse(gerador(), media_type=encoder.get_content_type())

    web_dist = Path(os.getenv("MYSTIQUE_WEB_DIST", Path(__file__).resolve().parent.parent / "web" / "dist"))
    if web_dist.is_dir():
        app.mount("/", StaticFiles(directory=web_dist, html=True), name="web")

    return app
