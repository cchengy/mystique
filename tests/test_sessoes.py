"""Session persistence and context regression tests."""

import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from servidor.sessoes import Sessoes


def test_sessions_are_account_scoped_and_reopen_with_messages() -> None:
    with tempfile.TemporaryDirectory() as pasta:
        store = Sessoes(Path(pasta))
        sessao = store.criar("auth0|alice", titulo="Primeiro contato")
        store.adicionar("auth0|alice", sessao["id"], "user", "Oi")
        store.adicionar("auth0|alice", sessao["id"], "assistant", "Olá")

        assert store.obter("auth0|alice", sessao["id"])["mensagens"] == [
            {"role": "user", "content": "Oi"},
            {"role": "assistant", "content": "Olá"},
        ]
        assert store.obter("auth0|bob", sessao["id"]) is None


def test_context_excludes_failed_system_notices() -> None:
    with tempfile.TemporaryDirectory() as pasta:
        store = Sessoes(Path(pasta))
        sessao = store.criar("alice")
        store.adicionar("alice", sessao["id"], "user", "mensagem anterior")
        store.adicionar("alice", sessao["id"], "assistant", "resposta anterior")
        store.adicionar("alice", sessao["id"], "system", "erro transitório")

        assert store.contexto("alice", sessao["id"]) == [
            {"role": "user", "content": "mensagem anterior"},
            {"role": "assistant", "content": "resposta anterior"},
        ]


def test_reasoning_traces_are_exposed_as_evidence_not_model_context() -> None:
    with tempfile.TemporaryDirectory() as pasta:
        store = Sessoes(Path(pasta))
        sessao = store.criar("alice", modo="evil")
        store.adicionar_evidencia("alice", sessao["id"], {
            "id": "trace-1", "outcome": "failure", "description": "guess",
            "content": "judge evidence", "agent_id": "byte",
        })

        loaded = store.obter("alice", sessao["id"])
        assert loaded["modo"] == "evil"
        assert loaded["evidencias"][0]["content"] == "judge evidence"
        assert store.contexto("alice", sessao["id"]) == []


def test_legacy_browser_chat_can_be_imported_once() -> None:
    with tempfile.TemporaryDirectory() as pasta:
        store = Sessoes(Path(pasta))
        imported = store.importar("alice", [
            {"role": "user", "content": "Oi"},
            {"role": "assistant", "content": "Olá"},
        ])
        assert imported["titulo"] == "Oi"
        assert len(store.listar("alice")) == 1
