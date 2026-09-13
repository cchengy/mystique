"""ReasoningBank: what she tried, what worked, what did not, and why.

Schema copied from Istara's ReasoningBank (frontend/src/lib/reasoningBankTypes.ts):
outcome, title, description, content, tags, domain, evidence_refs, judge_score,
confidence, status, usage_count, timestamps. Same field names, so traces written
here are portable to that system.

What it is for
--------------
Mystique identifies an ability by describing what she saw and convincing a judge.
She is often wrong the first time. Today that failure is thrown away. Here it is
kept, with the judge's verdict as evidence, so the next attempt on the same agent
starts from what already failed instead of repeating it.

Two things make this a bank and not a log:
  * every entry carries an OUTCOME (success or failure) and the evidence for it;
  * entries are RETRIEVED before the next attempt, and their usage_count grows,
    so what actually gets reused is visible.

Storage is one JSON file per entry under <workspace>/bank/, plus a human-readable
WIKI.md - the wiki is the traceable surface a person reads, the JSON is what the
agent queries. Writes are atomic and owner-only, the wiki is flushed once per
mission by `publicar()`, and the bank is bounded per agent.
"""

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

ESQUEMA = "istara.reasoningbank.v1"


@dataclass
class Traco:
    """One reasoning trace. Field names follow Istara's ReasoningMemoryItem."""

    id: str
    agent_id: str          # the world agent this is about
    source_kind: str       # "identificacao" | "consentimento" | "conquista"
    source_id: str
    outcome: str           # "success" | "failure"
    title: str
    description: str       # what she believed
    content: str           # why it went that way (the judge's words, verbatim)
    tags: list[str] = field(default_factory=list)
    domain: str = "capability-discovery"
    evidence_refs: list = field(default_factory=list)
    judge_score: float | None = None
    confidence: float = 0.5
    status: str = "active"
    usage_count: int = 0
    created_at: str = ""
    schema: str = ESQUEMA


def _agora() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


# Traces are cheap to write and cheap to read, but not free: the wiki is rebuilt
# from all of them, and recall reads all of them. Past this many for one agent the
# oldest failures that have already been superseded by a success are pruned - what
# recall needs is the recent failures, and the success ends the line of enquiry.
MAX_POR_AGENTE = 40


class Banco:
    def __init__(self, workspace: Path) -> None:
        self.pasta = workspace / "bank"
        self.pasta.mkdir(parents=True, exist_ok=True)
        # Corrupt files are skipped on read. Counting them means a trace that
        # vanished is visible in the summary instead of silently gone.
        self.ilegiveis = 0
        self._wiki_suja = False

    # --- disco -----------------------------------------------------------
    def _escrever(self, destino: Path, dados: dict) -> None:
        """Atomic, and owner-only - the same contract as sessions and accounts.

        A direct write leaves a half-written trace behind after a crash, and
        `todos()` would then skip it without a word.
        """
        temporario = destino.with_suffix(".tmp")
        temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        temporario.replace(destino)
        destino.chmod(0o600)

    # --- escrita ---------------------------------------------------------
    def registrar(self, *, agent_id: str, source_kind: str, outcome: str, title: str,
                  description: str, content: str, tags=None, judge_score=None,
                  confidence: float = 0.5) -> "Traco":
        t = Traco(
            id=uuid.uuid4().hex[:12], agent_id=agent_id, source_kind=source_kind,
            source_id=f"{agent_id}:{int(time.time())}", outcome=outcome, title=title,
            description=description, content=content, tags=list(tags or []),
            evidence_refs=[{"kind": "judge_verdict", "text": content[:500]}],
            judge_score=judge_score, confidence=confidence, created_at=_agora(),
        )
        self._escrever(self.pasta / f"{t.id}.json", asdict(t))
        self._podar(agent_id)
        self._wiki_suja = True
        self.publicar()
        return t

    def _podar(self, agent_id: str) -> None:
        """Keep the bank bounded without losing what recall actually reads."""
        itens = [t for t in self.todos() if t.get("agent_id") == agent_id]
        if len(itens) <= MAX_POR_AGENTE:
            return
        itens.sort(key=lambda t: t.get("created_at", ""))
        # Failures before the newest success are answered questions; drop those
        # first, oldest first, and only then the oldest entries of any kind.
        sucesso = max((i for i, t in enumerate(itens) if t.get("outcome") == "success"), default=-1)
        descartaveis = [t for t in itens[:sucesso] if t.get("outcome") == "failure"] or itens
        for t in descartaveis[: len(itens) - MAX_POR_AGENTE]:
            (self.pasta / f"{t['id']}.json").unlink(missing_ok=True)

    # --- leitura ---------------------------------------------------------
    def todos(self) -> list[dict]:
        saida = []
        ilegiveis = 0
        for arquivo in sorted(self.pasta.glob("*.json")):
            try:
                saida.append(json.loads(arquivo.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                ilegiveis += 1  # a corrupted entry must not break recall, but it is not invisible
        self.ilegiveis = ilegiveis
        return saida

    def recordar(self, agent_id: str, limite: int = 5) -> str:
        """What she already tried on this agent, in HER OWN words.

        CRITICAL: this is read back into Mystique's context, so it must never
        include `content` - that field holds the judge's verdict, and the judge
        knows the answer key. Only her own past descriptions and the outcome go
        back. The verdict stays on disk, for the wiki and for humans.
        """
        itens = [t for t in self.todos() if t.get("agent_id") == agent_id]
        if not itens:
            return ""
        itens.sort(key=lambda t: (t.get("outcome") != "failure", t.get("created_at", "")), reverse=False)
        linhas = []
        for t in itens[:limite]:
            marca = "✗ did not work" if t.get("outcome") == "failure" else "✓ worked"
            linhas.append(f"- [{marca}] you described it as \"{t.get('description','')}\"")
            self._usar(t)
        return ("What you already tried with this agent (do not repeat the failures):\n"
                + "\n".join(linhas))

    def _usar(self, t: dict) -> None:
        t["usage_count"] = int(t.get("usage_count", 0)) + 1
        try:
            self._escrever(self.pasta / f"{t['id']}.json", t)
        except OSError:
            pass
        # Deferred: recalling five traces used to rebuild the whole wiki five times.
        self._wiki_suja = True

    def resumo(self) -> dict:
        itens = self.todos()
        return {
            "total": len(itens),
            "outcomes": {o: sum(1 for t in itens if t.get("outcome") == o)
                         for o in {t.get("outcome") for t in itens}},
            "source_kinds": {k: sum(1 for t in itens if t.get("source_kind") == k)
                             for k in {t.get("source_kind") for t in itens}},
            "most_reused": max((t.get("usage_count", 0) for t in itens), default=0),
            "unreadable": self.ilegiveis,
        }

    # --- wiki ------------------------------------------------------------
    def publicar(self) -> Path | None:
        """Flush the wiki if anything changed since the last flush.

        Writing it on every single change made the cost quadratic in the size of
        the bank. Callers mark it dirty and flush once, at the end of a mission.
        """
        if not self._wiki_suja:
            return self.wiki if self.wiki.exists() else None
        self._reescrever_wiki()
        self._wiki_suja = False
        return self.wiki if self.wiki.exists() else None

    @property
    def wiki(self) -> Path:
        return self.pasta.parent / "WIKI.md"

    def _reescrever_wiki(self) -> None:
        """A human-readable page, rebuilt on every write. This is the traceability
        surface: what was learned, from whom, and whether it held up."""
        itens = self.todos()
        por_agente: dict[str, list[dict]] = {}
        for t in itens:
            por_agente.setdefault(t.get("agent_id", "?"), []).append(t)
        r = self.resumo()
        ilegiveis = f" · unreadable: {r['unreadable']}" if r.get("unreadable") else ""
        linhas = [
            "# What Mystique has learned", "",
            f"{r['total']} reasoning traces · outcomes: {r['outcomes']} · most reused: {r['most_reused']}×{ilegiveis}", "",
            "Written automatically. Each entry is an attempt she made, the judge's verdict,",
            "and whether it held. Failures are kept on purpose: they are what she reads first.", "",
        ]
        for agente, ts in sorted(por_agente.items()):
            linhas.append(f"## {agente}")
            for t in sorted(ts, key=lambda x: x.get("created_at", "")):
                marca = "✗" if t.get("outcome") == "failure" else "✓"
                linhas.append(f"- {marca} **{t.get('title','')}** — she thought: *{t.get('description','')}*")
                linhas.append(f"  - verdict: {t.get('content','')[:300]}")
                linhas.append(f"  - reused {t.get('usage_count',0)}× · confidence {t.get('confidence')}")
            linhas.append("")
        try:
            self.wiki.write_text("\n".join(linhas), encoding="utf-8")
            self.wiki.chmod(0o600)
        except OSError:
            pass
