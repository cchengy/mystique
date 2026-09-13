"""FastAPI app: REST + SSE (AG-UI protocol) for the trust-broker panel."""

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path

from ag_ui.encoder import EventEncoder
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from mystique.agente import FerramentasExtras, executar

from . import contas, cofre_client
from .eventos import evento_custom, evento_snapshot
from .mundo_servidor import InterrompivelMixin
from .mundos import ANONIMO, Mundos
from .sessoes import Sessoes

_ORCAMENTO_PADRAO = float(os.getenv("MYSTIQUE_BUDGET_USD", "5"))


class ChaveBody(BaseModel):
    chave: str | None = None          # colada à mão
    codigo: str | None = None         # OAuth PKCE do OpenRouter
    verificador: str | None = None
    metodo: str = "S256"


class ChaveProvedorBody(BaseModel):
    chave: str


class DecisaoBody(BaseModel):
    decisao: str  # "aprovar" | "rejeitar"


class MissaoBody(BaseModel):
    mensagem: str
    orcamento: float | None = None
    sessao_id: str
    idioma: str = "en"   # the language the UI is being read in


# She must answer in the language the person is reading, not in whatever the
# persona happens to be written in. English is the source language, so it needs
# no instruction at all.
_IDIOMAS = {
    "pt": ("\n\nAll visible communication must be in natural Brazilian Portuguese. "
           "Talk to the agents and deliver the final answer in Brazilian Portuguese only."),
    "en": "",
}


class SessaoBody(BaseModel):
    titulo: str = "New conversation"
    modo: str = "good"


class MensagemImportada(BaseModel):
    role: str
    content: str


class ImportarSessaoBody(BaseModel):
    mensagens: list[MensagemImportada]
    modo: str = "good"


class ModeloBody(BaseModel):
    modelo: str


class ApagarContaBody(BaseModel):
    confirmacao: str


def criar_app(mundos: Mundos, persona: str, extras: FerramentasExtras) -> FastAPI:
    if os.getenv("MYSTIQUE_REQUIRE_AUTH", "").lower() in {"1", "true", "yes"} and not contas.auth_configurada():
        raise RuntimeError("MYSTIQUE_REQUIRE_AUTH is enabled but Auth0 is not configured")
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
    tarefas_por_conta: dict[str, set[asyncio.Task]] = {}
    sessoes = Sessoes(contas.CONTAS_DIR)

    async def _sub_do_pedido(request: Request) -> str:
        usuario = await _exigir_conta(request)
        return usuario.get("sub", ANONIMO)

    def publicar(mundo, nome: str, valor: dict) -> None:
        eventos = getattr(mundo, "_eventos", None)
        if eventos is not None:
            eventos.publicar_nowait(evento_custom(nome, valor))

    async def _exigir_conta(request: Request) -> dict:
        """The live chat needs an account. The guided replay never calls this."""
        if not contas.auth_configurada():
            if os.getenv("MYSTIQUE_REQUIRE_AUTH", "").lower() in {"1", "true", "yes"}:
                raise HTTPException(503, "Authentication is required but Auth0 is not configured.")
            # No tenant configured: the deployment is open on purpose (local dev).
            return {"sub": "anonimo", "aberto": True}
        usuario = await contas.usuario_do_token(request.headers.get("authorization"))
        if usuario is None:
            raise HTTPException(401, "Sign in to use the live chat.")
        emitido = usuario.get("auth_time") or usuario.get("iat")
        instante = datetime.fromtimestamp(emitido, timezone.utc) if isinstance(emitido, (int, float)) else None
        contas.registrar_acesso(usuario.get("sub", ANONIMO), instante)
        return usuario

    async def _encerrar_conta(sub: str) -> None:
        tarefas = list(tarefas_por_conta.pop(sub, set()))
        for tarefa in tarefas:
            tarefa.cancel()
        if tarefas:
            await asyncio.gather(*tarefas, return_exceptions=True)
        await mundos.apagar(sub)

    @app.on_event("startup")
    async def iniciar_expiracao() -> None:
        async def varrer() -> None:
            while True:
                for sub in contas.contas_vencidas():
                    await _encerrar_conta(sub)
                    contas.apagar_conta(sub)
                await asyncio.sleep(3600)
        tarefa = asyncio.create_task(varrer())
        tarefas_em_curso.add(tarefa)
        tarefa.add_done_callback(tarefas_em_curso.discard)

    @app.get("/api/config")
    def config() -> dict:
        return {
            "modo": mundos.modo,
            # The front end needs this to decide whether to show the login at all.
            "auth": {
                "exigida": contas.auth_configurada(),
                "dominio": contas.AUTH0_DOMAIN or None,
                "audiencia": contas.AUTH0_AUDIENCE or None,
                "cliente": os.getenv("AUTH0_CLIENT_ID") or None,
            },
            "cofre": True,
        }

    @app.get("/api/eu")
    async def eu(request: Request) -> dict:
        usuario = await _exigir_conta(request)
        sub = usuario.get("sub", "anonimo")
        conta = contas.ler_conta(sub)
        credenciais = await cofre_client.pedir("GET", "/credentials", request.headers.get("authorization"))
        return {
            "sub": sub,
            "email": usuario.get("email"),
            "nome": usuario.get("name") or usuario.get("nickname"),
            "chave": credenciais.get("openrouter", {"tem": False}),
            "exa": credenciais.get("exa", {"tem": False}),
            "modelo": contas.modelo_da_conta(sub),
            "ciclo": {
                "ultimo_acesso": conta.get("last_access_at"),
                "apagar_em": conta.get("delete_after"),
                "dias_inatividade": 60,
            },
        }

    @app.delete("/api/conta", status_code=204)
    async def apagar_conta(corpo: ApagarContaBody, request: Request) -> None:
        usuario = await _exigir_conta(request)
        if corpo.confirmacao != "APAGAR MINHA CONTA":
            raise HTTPException(400, "Type APAGAR MINHA CONTA to confirm permanent deletion.")
        sub = usuario.get("sub", ANONIMO)
        await _encerrar_conta(sub)
        await cofre_client.pedir("DELETE", "/account", request.headers.get("authorization"))
        contas.apagar_conta(sub)

    @app.get("/api/openrouter/inicio")
    async def openrouter_inicio(request: Request) -> dict:
        """Where to send the browser so the user authorises on OpenRouter itself.
        They never paste a secret: the code comes back and we exchange it."""
        await _exigir_conta(request)
        return {
            "autorizar": "https://openrouter.ai/auth",
            "parametros": ["callback_url", "code_challenge", "code_challenge_method=S256"],
            "modelos": f"{contas.OPENROUTER}/models",
        }

    @app.post("/api/openrouter/chave")
    async def openrouter_chave(corpo: ChaveBody, request: Request) -> dict:
        await _exigir_conta(request)
        guardada = await cofre_client.pedir("PUT", "/credentials/openrouter", request.headers.get("authorization"), {
            "key": corpo.chave, "code": corpo.codigo, "verifier": corpo.verificador, "method": corpo.metodo,
        })
        estado = await cofre_client.pedir("GET", "/openrouter/api/v1/key", request.headers.get("authorization"))
        return {"guardada": guardada, "estado": {"chave": estado.get("data", {})}}

    @app.get("/api/openrouter/estado")
    async def openrouter_estado(request: Request) -> dict:
        await _exigir_conta(request)
        estado = await cofre_client.pedir("GET", "/openrouter/api/v1/key", request.headers.get("authorization"))
        return {"chave": estado.get("data", {})}

    @app.delete("/api/openrouter/chave", status_code=204)
    async def openrouter_esquecer(request: Request) -> None:
        await _exigir_conta(request)
        await cofre_client.pedir("DELETE", "/credentials/openrouter", request.headers.get("authorization"))

    @app.put("/api/exa/chave")
    async def exa_chave(corpo: ChaveProvedorBody, request: Request) -> dict:
        await _exigir_conta(request)
        return await cofre_client.pedir("PUT", "/credentials/exa", request.headers.get("authorization"), {"key": corpo.chave})

    @app.delete("/api/exa/chave", status_code=204)
    async def exa_esquecer(request: Request) -> None:
        await _exigir_conta(request)
        await cofre_client.pedir("DELETE", "/credentials/exa", request.headers.get("authorization"))

    @app.put("/api/openrouter/modelo")
    async def openrouter_modelo(corpo: ModeloBody, request: Request) -> dict:
        usuario = await _exigir_conta(request)
        modelo = corpo.modelo.strip()
        if not modelo or len(modelo) > 200 or any(c.isspace() for c in modelo):
            raise HTTPException(400, "Invalid OpenRouter model id.")
        contas.guardar_modelo(usuario.get("sub", "anonimo"), modelo)
        return {"modelo": modelo}

    @app.get("/api/sessoes")
    async def listar_sessoes(request: Request) -> list[dict]:
        return sessoes.listar(await _sub_do_pedido(request))

    @app.post("/api/sessoes", status_code=201)
    async def criar_sessao(corpo: SessaoBody, request: Request) -> dict:
        if corpo.modo not in {"good", "evil"}:
            raise HTTPException(400, "modo must be good or evil")
        return sessoes.criar(await _sub_do_pedido(request), titulo=corpo.titulo, modo=corpo.modo)

    @app.post("/api/sessoes/importar", status_code=201)
    async def importar_sessao(corpo: ImportarSessaoBody, request: Request) -> dict:
        if corpo.modo not in {"good", "evil"} or len(corpo.mensagens) > 80:
            raise HTTPException(400, "Invalid legacy session")
        mensagens = [{"role": m.role, "content": m.content} for m in corpo.mensagens]
        if any(m["role"] not in {"user", "assistant"} or len(m["content"]) > 20000 for m in mensagens):
            raise HTTPException(400, "Invalid legacy message")
        return sessoes.importar(await _sub_do_pedido(request), mensagens, corpo.modo)

    @app.get("/api/sessoes/{sessao_id}")
    async def obter_sessao(sessao_id: str, request: Request) -> dict:
        sessao = sessoes.obter(await _sub_do_pedido(request), sessao_id)
        if sessao is None:
            raise HTTPException(404, "Session not found")
        return sessao

    @app.post("/api/missoes", status_code=202)
    async def iniciar_missao(corpo: MissaoBody, request: Request) -> dict:
        authorization = request.headers.get("authorization")
        sub = await _sub_do_pedido(request)
        sessao = sessoes.obter(sub, corpo.sessao_id)
        if sessao is None:
            raise HTTPException(404, "Session not found")
        modo = sessao["modo"]
        mundo = mundos.para(sub, modo)
        contexto = sessoes.contexto(sub, corpo.sessao_id)
        sessoes.adicionar(sub, corpo.sessao_id, "user", corpo.mensagem)
        banco = getattr(mundo, "banco", None)
        evidencias_antes = {item.get("id"): item for item in banco.todos()} if banco is not None else {}
        openai_config = None
        if authorization:
            openai_config = {
                "base_url": f"{cofre_client.COFRE_URL}/openrouter/api/v1",
                "modelo": contas.modelo_da_conta(sub),
                "chave": authorization.removeprefix("Bearer "),
            }
            mundo.configurar_openai(**openai_config)
        async def executar_com_estado() -> None:
            from mystique.poderes import configurar_broker_exa
            reset_exa = configurar_broker_exa(
                cofre_client.COFRE_URL, openai_config["chave"]
            ) if openai_config else (lambda: None)
            iniciar_ui = getattr(mundo, "iniciar_missao_ui", None)
            if iniciar_ui:
                iniciar_ui()
            publicar(mundo, "missao_iniciada", {"mensagem": corpo.mensagem})
            try:
                persona_modo, extras_modo = mundos.contexto(modo)
                persona_idioma = persona_modo + _IDIOMAS.get(corpo.idioma, "")
                await executar(
                    corpo.mensagem, mundo, corpo.orcamento or _ORCAMENTO_PADRAO, False,
                    persona_idioma, extras_modo, openai_config=openai_config, historico=contexto,
                )
            finally:
                reset_exa()
                if openai_config:
                    await mundo.desconfigurar_openai()
                finalizar_ui = getattr(mundo, "finalizar_missao_ui", None)
                if finalizar_ui:
                    texto, erro = finalizar_ui()
                    sessoes.adicionar(sub, corpo.sessao_id, "system" if erro else "assistant", texto)
                    if banco is not None:
                        for evidencia in banco.todos():
                            anterior = evidencias_antes.get(evidencia.get("id"))
                            if anterior is None or anterior.get("usage_count") != evidencia.get("usage_count"):
                                sessoes.adicionar_evidencia(sub, corpo.sessao_id, evidencia)
                    publicar(mundo, "resposta_final", {"texto": texto, "erro": erro})
                publicar(mundo, "missao_finalizada", {"eof": True})

        tarefa = asyncio.create_task(executar_com_estado())
        tarefas_em_curso.add(tarefa)
        tarefas_por_conta.setdefault(sub, set()).add(tarefa)
        def concluir(t: asyncio.Task) -> None:
            tarefas_em_curso.discard(t)
            tarefas_por_conta.get(sub, set()).discard(t)
        tarefa.add_done_callback(concluir)
        return {"ok": True}

    @app.post("/api/recibos/{recibo_id}/decisao")
    async def decidir_recibo(recibo_id: str, corpo: DecisaoBody, request: Request) -> dict:
        if corpo.decisao not in ("aprovar", "rejeitar"):
            raise HTTPException(400, "decisao must be 'aprovar' or 'rejeitar'")
        # The receipt belongs to whichever world raised it, and an Evil session's
        # receipt is not in the Good world. The request does not carry the mode,
        # so ask every world this account actually has open.
        sub = await _sub_do_pedido(request)
        for mundo in mundos.existentes(sub) or [mundos.para(sub)]:
            if mundo.decidir(recibo_id, corpo.decisao == "aprovar"):
                return {"ok": True}
        raise HTTPException(409, "receipt not found, already resolved, or not approved by the judge")

    @app.get("/agui/stream")
    async def stream(request: Request) -> StreamingResponse:
        # Fetch streaming carries the bearer token in a header. Never put access
        # tokens in URLs: reverse proxies and access logs routinely retain them.
        autorizacao = request.headers.get("authorization")
        if contas.auth_configurada():
            usuario = await contas.usuario_do_token(autorizacao)
            if usuario is None:
                raise HTTPException(401, "Sign in to watch the live stream.")
            sub = usuario.get("sub", ANONIMO)
        elif os.getenv("MYSTIQUE_REQUIRE_AUTH", "").lower() in {"1", "true", "yes"}:
            raise HTTPException(503, "Authentication is required but Auth0 is not configured.")
        else:
            sub = ANONIMO
        mundo = mundos.para(sub)
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
