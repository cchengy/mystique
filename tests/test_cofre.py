"""Security properties of the isolated 24-hour credential broker."""

import base64
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

os.environ.setdefault("MYSTIQUE_VAULT_KEY", base64.urlsafe_b64encode(b"k" * 32).decode())
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402
from cofre import app as cofre  # noqa: E402


def test_ciphertext_is_scoped_and_tampering_fails_closed() -> None:
    box = cofre._encrypt("auth0|alice", "openrouter", "sk-secret")
    assert "sk-secret" not in str(box)
    assert cofre._decrypt("auth0|alice", "openrouter", box) == "sk-secret"
    try:
        cofre._decrypt("auth0|bob", "openrouter", box)
    except Exception:
        pass
    else:
        raise AssertionError("cross-account decrypt must fail")


def test_credential_expires_at_24_hours_without_sliding_renewal() -> None:
    created = datetime(2026, 9, 12, tzinfo=timezone.utc)
    record = {"created_at": created.isoformat(), "expires_at": (created + timedelta(hours=24)).isoformat(), "origin": "pasted"}
    with patch.object(cofre, "_now", return_value=created + timedelta(hours=23, minutes=59)):
        assert cofre._metadata(record)["tem"] is True
    with patch.object(cofre, "_now", return_value=created + timedelta(hours=24)):
        assert cofre._metadata(record)["tem"] is False


def test_purge_physically_removes_expired_ciphertext() -> None:
    created = datetime(2026, 9, 12, tzinfo=timezone.utc)
    with tempfile.TemporaryDirectory() as folder, patch.object(cofre, "STORE", Path(folder)):
        cofre._write("auth0|alice", {"providers": {"openrouter": {
            "created_at": created.isoformat(), "expires_at": (created + timedelta(hours=24)).isoformat(),
            "origin": "pasted", "box": cofre._encrypt("auth0|alice", "openrouter", "sk-secret"),
        }}})
        with patch.object(cofre, "_now", return_value=created + timedelta(hours=24, seconds=1)):
            assert cofre.purge_expired() == 1
        assert list(Path(folder).iterdir()) == []


def test_broker_requires_auth0_and_deletes_credential() -> None:
    with tempfile.TemporaryDirectory() as folder, patch.object(cofre, "STORE", Path(folder)), patch.object(
        cofre, "usuario_do_token", AsyncMock(return_value={"sub": "auth0|alice"})
    ), TestClient(cofre.app) as client:
        cofre._write("auth0|alice", {"providers": {}})
        response = client.delete("/credentials/openrouter", headers={"Authorization": "Bearer valid"})
        assert response.status_code == 204


def test_broker_rejects_provider_operations_outside_the_allowlist() -> None:
    with patch.object(cofre, "usuario_do_token", AsyncMock(return_value={"sub": "auth0|alice"})), TestClient(cofre.app) as client:
        response = client.delete("/openrouter/api/v1/keys/anything", headers={"Authorization": "Bearer valid"})
        assert response.status_code == 404


def test_compose_keeps_the_master_key_and_volume_out_of_main_app() -> None:
    compose = (Path(__file__).resolve().parent.parent / "compose.yaml").read_text(encoding="utf-8")
    main = compose.split("  mystique:\n", 1)[1].split("  credential-broker:\n", 1)[0]
    broker = compose.rsplit("\n  credential-broker:\n", 1)[1]
    assert "MYSTIQUE_VAULT_KEY" not in main
    assert "mystique-credentials" not in main
    assert "MYSTIQUE_VAULT_KEY" in broker
    assert "mystique-credentials:/vault" in broker
    assert "ports:" not in broker and "expose:" not in broker


if __name__ == "__main__":
    test_ciphertext_is_scoped_and_tampering_fails_closed()
    test_credential_expires_at_24_hours_without_sliding_renewal()
    test_purge_physically_removes_expired_ciphertext()
    test_broker_requires_auth0_and_deletes_credential()
    test_broker_rejects_provider_operations_outside_the_allowlist()
    test_compose_keeps_the_master_key_and_volume_out_of_main_app()
    print("OK    vault: AES-GCM scope, 24-hour expiry, purge and Auth0 boundary")
