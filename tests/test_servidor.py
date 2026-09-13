"""Regression checks for the HTTP bridge used by the live Mystique UI."""

import asyncio
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from servidor.app import criar_app  # noqa: E402
from servidor import contas  # noqa: E402
from servidor.mundo_servidor import _evento_publico  # noqa: E402
from mystique.mundo import Mundo  # noqa: E402


def test_production_mode_fails_closed_without_auth0() -> None:
    with patch.dict(os.environ, {"MYSTIQUE_REQUIRE_AUTH": "true"}), patch(
        "servidor.app.contas.auth_configurada", return_value=False
    ):
        try:
            criar_app(SimpleNamespace(modo="good"), "persona", lambda _: [])
        except RuntimeError:
            pass
        else:
            raise AssertionError("production must not start without Auth0")


def test_expired_account_deletion_removes_file_and_workspace() -> None:
    with tempfile.TemporaryDirectory() as pasta, patch.object(contas, "CONTAS_DIR", Path(pasta)):
        sub = "auth0|inactive"
        contas.gravar_conta(sub, {"last_access_at": "2026-01-01T00:00:00+00:00"})
        workspace = contas.workspace_da_conta(sub)
        workspace.mkdir(parents=True)
        (workspace / "private.json").write_text("secret", encoding="utf-8")

        removidas = contas.expirar_contas_inativas(agora="2026-03-03T00:00:01+00:00")

        assert removidas == 1
        assert not contas._arquivo(sub).exists()
        assert not workspace.parent.exists()


def test_user_can_delete_all_application_account_data() -> None:
    mundos = SimpleNamespace(modo="good", apagar=AsyncMock())
    app = criar_app(mundos, "persona", lambda _: [])
    with tempfile.TemporaryDirectory() as pasta:
        with (
            patch.object(contas, "CONTAS_DIR", Path(pasta)),
            patch("servidor.app.contas.auth_configurada", return_value=True),
            patch("servidor.app.contas.usuario_do_token", AsyncMock(return_value={"sub": "auth0|alice"})),
            patch("servidor.app.cofre_client.pedir", AsyncMock(return_value={})),
            TestClient(app) as client,
        ):
            contas.gravar_conta("auth0|alice", {"last_access_at": "2026-09-12T00:00:00+00:00"})
            response = client.request(
                "DELETE", "/api/conta", headers={"Authorization": "Bearer access-token"},
                json={"confirmacao": "APAGAR MINHA CONTA"},
            )

            assert response.status_code == 204
            assert not contas._arquivo("auth0|alice").exists()


def test_public_stream_keeps_dialogue_and_redacts_internal_traces() -> None:
    assert _evento_publico("🔧 usar_poder({secret})") == ("status", {"texto": "Pensando"})
    assert _evento_publico("💬 Mystique → Byte: Can you inspect this?") == (
        "dialogo", {"de": "Mystique", "para": "Byte", "texto": "Can you inspect this?"}
    )
    assert _evento_publico("💬 Byte: Yes, send the error.") == (
        "dialogo", {"de": "Byte", "para": "Mystique", "texto": "Yes, send the error."}
    )
    assert _evento_publico("[Mystique] The final answer") == (
        "resposta", {"texto": "The final answer"}
    )
    assert _evento_publico("[Mystique] Resposta **final**\\</｜｜DSML｜｜ parameter>") == (
        "resposta", {"texto": "Resposta final"}
    )


def test_mission_is_scheduled_on_the_application_event_loop() -> None:
    mundo = SimpleNamespace(modo="good")
    mundos = SimpleNamespace(modo="good", para=lambda _sub, _modo=None: mundo, contexto=lambda _modo=None: ("persona", lambda _: []))
    executar = AsyncMock()
    app = criar_app(mundos, "persona", lambda _: [])

    with patch("servidor.app.executar", executar), TestClient(app, raise_server_exceptions=False) as client:
        session = client.post("/api/sessoes", json={"titulo": "Test", "modo": "good"}).json()
        response = client.post("/api/missoes", json={"mensagem": "Meet Byte", "sessao_id": session["id"]})
        for _ in range(10):
            if executar.await_count:
                break
            asyncio.run(asyncio.sleep(0.01))

    assert response.status_code == 202
    executar.assert_awaited_once()


def test_authenticated_mission_uses_the_broker_without_loading_the_provider_key() -> None:
    mundo = SimpleNamespace(modo="good", configurar_openai=lambda **_config: None, desconfigurar_openai=AsyncMock())
    mundos = SimpleNamespace(modo="good", para=lambda _sub, _modo=None: mundo, contexto=lambda _modo=None: ("persona", lambda _: []))
    executar = AsyncMock()
    app = criar_app(mundos, "persona", lambda _: [])

    with (
        patch("servidor.app.contas.auth_configurada", return_value=True),
        patch("servidor.app.contas.usuario_do_token", AsyncMock(return_value={"sub": "auth0|alice"})),
        patch("servidor.app.contas.modelo_da_conta", return_value="openai/gpt-5-mini"),
        patch("servidor.app.executar", executar),
        TestClient(app, raise_server_exceptions=False) as client,
    ):
        session = client.post(
            "/api/sessoes",
            headers={"Authorization": "Bearer access-token"},
            json={"titulo": "Teste", "modo": "good"},
        ).json()
        response = client.post(
            "/api/missoes",
            headers={"Authorization": "Bearer access-token"},
            json={"mensagem": "Meet Byte", "sessao_id": session["id"]},
        )
        for _ in range(10):
            if executar.await_count:
                break
            asyncio.run(asyncio.sleep(0.01))

    assert response.status_code == 202
    assert executar.await_args.kwargs["openai_config"] == {
        "base_url": "http://credential-broker:8001/openrouter/api/v1",
        "modelo": "openai/gpt-5-mini",
        "chave": "access-token",
    }
    assert executar.await_args.kwargs["historico"] == []


def test_authenticated_user_can_select_an_openrouter_model() -> None:
    mundos = SimpleNamespace(modo="good")
    app = criar_app(mundos, "persona", lambda _: [])

    with (
        patch("servidor.app.contas.auth_configurada", return_value=True),
        patch("servidor.app.contas.usuario_do_token", AsyncMock(return_value={"sub": "auth0|alice"})),
        patch("servidor.app.contas.guardar_modelo") as guardar_modelo,
        TestClient(app) as client,
    ):
        response = client.put(
            "/api/openrouter/modelo",
            headers={"Authorization": "Bearer access-token"},
            json={"modelo": "anthropic/claude-sonnet-4"},
        )

    assert response.status_code == 200
    guardar_modelo.assert_called_once_with("auth0|alice", "anthropic/claude-sonnet-4")


def test_world_can_use_the_accounts_openrouter_credentials() -> None:
    mundo = object.__new__(Mundo)
    mundo._cliente = None
    mundo.configurar_openai("https://openrouter.ai/api/v1", "openai/gpt-5-mini", "private-key")

    assert mundo._cliente._modelo == "openai/gpt-5-mini"


def test_local_frontend_origins_are_allowed_by_default() -> None:
    mundo = SimpleNamespace(modo="good")
    app = criar_app(mundo, "persona", lambda _: [])

    with TestClient(app) as client:
        for origem in ("http://localhost:5173", "http://127.0.0.1:5173"):
            response = client.options(
                "/api/missoes",
                headers={
                    "Origin": origem,
                    "Access-Control-Request-Method": "POST",
                },
            )
            assert response.status_code == 200
            assert response.headers["access-control-allow-origin"] == origem


def test_server_loads_provider_environment_before_importing_the_engine() -> None:
    raiz = Path(__file__).resolve().parent.parent
    ambiente = os.environ.copy()
    for nome in (
        "MYSTIQUE_PROVIDER",
        "MYSTIQUE_BASE_URL",
        "MYSTIQUE_MODEL_ID",
        "MYSTIQUE_WORLD_PROVIDER",
        "MYSTIQUE_WORLD_BASE_URL",
        "MYSTIQUE_WORLD_MODEL",
        "MYSTIQUE_WORLD_API_KEY",
    ):
        ambiente.pop(nome, None)
    resultado = subprocess.run(
        [sys.executable, "-c", "import servidor.__main__; from mystique.agente_local import ativo; assert ativo()"],
        cwd=raiz,
        env=ambiente,
        capture_output=True,
        text=True,
    )
    assert resultado.returncode == 0, resultado.stderr


def test_server_can_serve_the_built_main_ui() -> None:
    mundo = SimpleNamespace(modo="good")
    with tempfile.TemporaryDirectory() as pasta:
        dist = Path(pasta)
        (dist / "index.html").write_text("<h1>Mystique live</h1>", encoding="utf-8")
        with patch.dict(os.environ, {"MYSTIQUE_WEB_DIST": str(dist)}):
            app = criar_app(mundo, "persona", lambda _: [])
        with TestClient(app) as client:
            response = client.get("/")
    assert response.status_code == 200
    assert "Mystique live" in response.text


if __name__ == "__main__":
    test_production_mode_fails_closed_without_auth0()
    test_expired_account_deletion_removes_file_and_workspace()
    test_user_can_delete_all_application_account_data()
    test_public_stream_keeps_dialogue_and_redacts_internal_traces()
    test_mission_is_scheduled_on_the_application_event_loop()
    test_authenticated_mission_uses_the_broker_without_loading_the_provider_key()
    test_local_frontend_origins_are_allowed_by_default()
    test_server_loads_provider_environment_before_importing_the_engine()
    test_server_can_serve_the_built_main_ui()
    print("OK    server: public stream keeps dialogue and redacts internal traces")
    print("OK    server: mission is scheduled on the application event loop")
    print("OK    server: both local frontend origins are allowed by default")
    print("OK    server: provider environment is loaded before the engine")
    print("OK    server: built main UI is served by the same process")
    print("OK    server: expired and user-requested account deletion remove owned data")
