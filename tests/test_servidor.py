"""Regression checks for the HTTP bridge used by the live Mystique UI."""

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from servidor.app import criar_app  # noqa: E402


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


if __name__ == "__main__":
    test_mission_is_scheduled_on_the_application_event_loop()
    test_local_frontend_origins_are_allowed_by_default()
    test_server_loads_provider_environment_before_importing_the_engine()
    print("OK    server: mission is scheduled on the application event loop")
    print("OK    server: both local frontend origins are allowed by default")
    print("OK    server: provider environment is loaded before the engine")
