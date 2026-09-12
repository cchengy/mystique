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
from servidor.mundo_servidor import _evento_publico  # noqa: E402


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
    executar = AsyncMock()
    app = criar_app(mundo, "persona", lambda _: [])

    with patch("servidor.app.executar", executar), TestClient(app, raise_server_exceptions=False) as client:
        response = client.post("/api/missoes", json={"mensagem": "Meet Byte"})
        for _ in range(10):
            if executar.await_count:
                break
            asyncio.run(asyncio.sleep(0.01))

    assert response.status_code == 202
    executar.assert_awaited_once()


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
    test_public_stream_keeps_dialogue_and_redacts_internal_traces()
    test_mission_is_scheduled_on_the_application_event_loop()
    test_local_frontend_origins_are_allowed_by_default()
    test_server_loads_provider_environment_before_importing_the_engine()
    test_server_can_serve_the_built_main_ui()
    print("OK    server: public stream keeps dialogue and redacts internal traces")
    print("OK    server: mission is scheduled on the application event loop")
    print("OK    server: both local frontend origins are allowed by default")
    print("OK    server: provider environment is loaded before the engine")
    print("OK    server: built main UI is served by the same process")
