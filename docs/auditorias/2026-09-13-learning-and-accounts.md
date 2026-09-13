# Audit: Reasoning Bank, wiki, trajectories, persistence and account separation

Date: 2026-09-13 · Scope: `mystique/banco.py`, `mystique/mundo.py`, `servidor/` (accounts,
sessions, worlds, mission), `cofre/`, and the surfaces that display any of it.
Method: read of every call site plus the offline tests; three defects were reproduced with
new tests before being fixed.

## Summary

The chain is wired correctly end to end — one workspace per account and profile, one bank
per workspace, sessions and evidence keyed by the Auth0 `sub`, deletion that reaches every
artifact. Three real defects were found and fixed, the first of them serious: **the bank
was never read back to Mystique**, so the learning loop the product describes did not
close. Six lower-severity items are recorded as open, with recommendations.

## Fixed in this pass

### 1. The recall went to the judge, not to Mystique — the loop never closed

`_identificar` appended `banco.recordar(...)` to the `evidencia` string, which is passed to
`_julgar`. So her own past failed descriptions — and the literal sentence "do not repeat the
failures" — were sent to the **judge**, while Mystique received only the generic "the judge
did not recognize the ability". Two consequences:

- the documented mechanism ("entries are retrieved before the next attempt") did not exist:
  nothing from the bank ever entered her context, so nothing could change her next guess;
- an impartial evaluator that already knows the answer key was being told which
  descriptions to discount — bias, in the one place the design is careful to keep clean.

Now the recall is read **after** the verdict, only when she failed, and returned to her in
the tool result. The judge's own words still never reach her. Covered by
`tests/test_banco.py::test_recall_reaches_mystique_and_not_the_judge`.

### 2. `usage_count` counted attempts, not reuse

Recall ran on every identification, success included, incrementing `usage_count` on traces
nothing had actually used. The field is the bank's only evidence of "what gets reused", so
it was measuring the wrong thing. It now moves only when a trace is genuinely fed back.

### 3. Consent receipts could not be resolved in an Evil session

`POST /api/recibos/{id}/decisao` resolved the world with `mundos.para(sub)` — no mode — which
returns the deployment's default profile. A receipt raised inside an Evil session lives in
the Evil world, so approving it answered 409. The endpoint now asks every world the account
actually has open, without instantiating (and writing a workspace for) a profile it never
used.

## Verified correct

- **Account separation.** `Mundos` keys worlds by `(sub, modo)`; the workspace is
  `CONTAS_DIR/<sha256(sub)[:32]>/workspace` (`workspace-evil` for the other profile), so the
  bank, wiki, adapters and audits of one account are physically separate from another's.
  Event buses are per account by construction; Good and Evil deliberately share one bus so
  switching profile does not drop the live stream.
- **Sessions.** One JSON document per conversation under the same account directory, atomic
  writes, `chmod 600`, session ids rejected unless hex (no path traversal), import capped at
  80 messages and 20k characters each, model context capped at the last 40 turns.
- **Identity.** Every live route verifies the Auth0 JWT against the tenant JWKS —
  signature, issuer, audience, expiry — and the `sub` claim is the only account id. The
  stream carries the bearer in a header, never a query string. With `MYSTIQUE_REQUIRE_AUTH=true`
  and Auth0 incomplete the app refuses to serve rather than falling open.
- **Deletion.** `apagar_conta` removes the account file and the whole account directory —
  sessions, workspace, bank, wiki, adapters, audits — and the credential broker is told
  separately. Expiry cancels running missions and evicts worlds and provider clients before
  touching disk.
- **The secret holds.** `recordar` returns only her own descriptions and the outcome; the
  judge's verdict stays in `content`, on disk, for the wiki and for people.
- **Evidence projection.** A mission attaches to the session only the traces that are new or
  whose reuse changed, so the Compare view shows that run's reasoning rather than the whole
  bank.

## Open, with recommendations

| # | Finding | Why it matters | Recommendation |
|---|---|---|---|
| 4 | `WIKI.md` is written per account and never exposed | It is described as the traceability surface a person reads, and no one can read it | A read-only `GET /api/wiki` for the signed-in account, rendered in the rail |
| 5 | Bank writes are not atomic and not `chmod 600` | Sessions and accounts are both; a crash mid-write corrupts a trace, and `todos()` skips corrupt files silently, so it disappears without a word | tmp + `replace` + `chmod 600`, and count skipped files in `resumo()` |
| 6 | The wiki is rebuilt on every write *and* every recall | O(n²) writes as the bank grows; a recall of 5 traces rewrites the whole wiki 5 times | Rebuild once per mission, or mark dirty and flush at the end |
| 7 | The bank grows without bound | 60-day retention is the only limit; a heavy account accumulates traces and a wiki that is rewritten in full | Cap per agent, or prune superseded failures once the ability is earned |
| 8 | Two missions in one account and profile share one `Mundo` | `configurar_openai` is world-global and the first mission to finish runs `desconfigurar_openai` in its `finally`, pulling the model config out from under the second | One mission per account at a time (reject with 409), or per-mission provider config |
| 9 | The 60-day clock moves on token refresh, not only on sign-in | The UI says "60 days without a successful sign-in"; silent refresh renews it without anyone signing in | Either use `auth_time` only, or say "without use" in the copy |

None of the open items is a data-separation or secrecy problem. 4, 5 and 8 are the ones
worth doing next; 8 is the only one that can produce a wrong answer for a user.
