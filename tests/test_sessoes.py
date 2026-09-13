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


def test_a_new_account_starts_with_nothing() -> None:
    """A fresh account inherits nothing - not from the browser, not from anyone.

    The client used to import the pre-accounts transcript kept in localStorage
    into the first session it created, so signing up on a machine that still had
    one opened somebody else's conversation.
    """
    with tempfile.TemporaryDirectory() as pasta:
        store = Sessoes(Path(pasta))
        assert store.listar("auth0|newcomer") == []
        sessao = store.criar("auth0|newcomer")
        assert sessao["mensagens"] == []
        assert sessao["evidencias"] == []
        assert len(store.listar("auth0|newcomer")) == 1
        # and still nothing of anyone else's
        assert store.listar("auth0|someone-else") == []


def test_the_exchange_with_agents_is_kept_and_is_not_model_context() -> None:
    """The dialogue was only ever in the browser, so rebuilding the transcript at
    the end of a mission erased everything the person had just watched."""
    with tempfile.TemporaryDirectory() as pasta:
        store = Sessoes(Path(pasta))
        sessao = store.criar("auth0|alice")
        store.adicionar("auth0|alice", sessao["id"], "user", "Find me a recipe")
        store.adicionar_dialogo("auth0|alice", sessao["id"], "Mystique", "Byte", "What can you do?")
        store.adicionar_dialogo("auth0|alice", sessao["id"], "Byte", "Mystique", "I run code.")
        store.adicionar("auth0|alice", sessao["id"], "assistant", "Here is the recipe")

        guardadas = store.obter("auth0|alice", sessao["id"])["mensagens"]
        assert [m["role"] for m in guardadas] == ["user", "dialogo", "dialogo", "assistant"]
        assert guardadas[1]["de"] == "Mystique" and guardadas[1]["para"] == "Byte"
        # ...and none of it is fed back to the model as her own turns
        assert store.contexto("auth0|alice", sessao["id"]) == [
            {"role": "user", "content": "Find me a recipe"},
            {"role": "assistant", "content": "Here is the recipe"},
        ]


if __name__ == "__main__":
    test_sessions_are_account_scoped_and_reopen_with_messages()
    test_context_excludes_failed_system_notices()
    test_reasoning_traces_are_exposed_as_evidence_not_model_context()
    test_a_new_account_starts_with_nothing()
    test_the_exchange_with_agents_is_kept_and_is_not_model_context()
    print("OK    sessions: account-scoped, mode and evidence kept, a new account starts empty")
