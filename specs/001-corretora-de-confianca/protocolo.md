# Protocol — trust-broker panel (FR-011 / SC-005)

Two new processes sit on top of the unchanged engine (`mystique/`, `good/`, `evil/`):

```
servidor/  FastAPI + SSE, speaks AG-UI (ag-ui-protocol)   python -m servidor
frontend/  React + Vite, plain EventSource + fetch        npm run dev  (in frontend/)
```

## The one change to the engine

`mystique/mundo.py` gained a single hook, `_aguardar_aprovacao(...)`, called right after a
recognition attempt is judged and right before it would be persisted (`good/mundo.py`'s
`mapear_habilidade`, `evil/mundo.py`'s `roubar_poder`). Its default implementation returns
`True` immediately — `python -m good` / `python -m evil` are byte-for-byte the same as before.
`servidor/mundo_servidor.py` overrides it (via `InterrompivelMixin`, composed onto `MundoBem`/
`MundoMal` — no duplicated logic) to publish an event and block on a human decision.

## Shared state loop

On SSE connect, the backend sends one `STATE_SNAPSHOT` built from what `Mundo` already holds in
memory (`self.agentes` + `self.absorcoes` — no disk re-read). From then on, every state change
is pushed the instant it happens, at the points the engine already centralizes them
(`_salvar`, `conversar`, `descartar`): a fresh `STATE_SNAPSHOT` plus a small custom event for
the UI reaction that doesn't need a full snapshot re-render. No polling anywhere.

## Events (AG-UI over SSE)

| Event | `type` | When | Payload |
|---|---|---|---|
| Full state | `STATE_SNAPSHOT` | on connect; after every `_salvar`, `conversar` (new observation), `descartar` | `{modo, agentes: [{id, nome, apresentacao, externo, capacidades: [{id, estado, motivo}], descartado, essencia_absorvida, progresso}], absorcoes: {...}}` |
| Pending receipt | `CUSTOM` `recibo_pendente` | `_aguardar_aprovacao` is called (every recognition attempt, including ones the judge already rejected) | `{recibo_id, agente_id, descricao_alegada, evidencia, veredito: {aprovado, motivo}}` |
| Receipt closed | `CUSTOM` `recibo_resolvido` | a human decision resolves it, or the judge had already rejected it (auto-closed, non-blocking) | `{recibo_id, decisao: "aprovar" \| "rejeitar" \| "rejeitado_pelo_juiz"}` |
| New observation | `CUSTOM` `capacidade_observada` | `agente.observados` gains a new id inside `conversar` | `{agente_id, capacidade_id}` |
| Discard | `CUSTOM` `agente_descartado` | evil mode, `descartar`/full drain | `{agente_id}` |

`capacidade.estado` is one of `nao_observada | observada_pendente | confirmada | rejeitada` — an
enum, never the ability's real description before it is earned (FR-009). `descricao_alegada`/
`evidencia` in `recibo_pendente` are text Mystique herself generated when calling
`mapear_habilidade`/`roubar_poder`; exposing them to the human does not violate FR-009 (that
rule protects the *agent's* secret, never seen by Mystique before earning it — this is the
inverse, the human seeing what Mystique claimed).

## REST actions

- `POST /api/missoes` `{mensagem, orcamento?}` — starts one mission (`asyncio.create_task`, same
  one-shot semantics as `python -m good "mission"`). 202 Accepted.
- `POST /api/recibos/{recibo_id}/decisao` `{decisao: "aprovar" | "rejeitar"}` — resolves a
  pending receipt. 409 if the id is unknown, already resolved, or was never pending (judge
  already rejected it) — a backend guard, not just a disabled button in the UI.
- `GET /api/config` — `{modo: "good" | "evil"}`, read-only (set by `MYSTIQUE_MODO` at boot).

## Run it

```bash
pip install -r requirements.txt
MYSTIQUE_MODO=good python -m servidor   # or MYSTIQUE_MODO=evil; also accepts bem/mal
cd frontend && npm install && npm run dev
```

Optional env vars (all have working defaults): `SERVIDOR_PORTA` (backend port, default 8000),
`FRONTEND_ORIGIN` (CORS allow-origin, default `http://localhost:5173`), `VITE_API_BASE` in
`frontend/.env.local` (default `http://127.0.0.1:8000`). Not added to the shared `.env.example`
here since that file is claimed by `cchengy-claude` in `.coord/`.

## Known scope cuts (time-boxed build, see .coord/agents/ednan-claude.md)

- The frontend talks to the AG-UI/SSE stream directly (`EventSource` + `fetch`), not through the
  `@copilotkit/react-core` runtime — `useCopilotAction`'s HITL pattern is built for the *copilot*
  to decide to call a frontend action, not for a server-pushed pending decision, so a plain
  component listening to `recibo_pendente` is the correct shape here, not a fallback taken only
  under time pressure.
- Mystique's own narration text (what she says to each agent) is not bridged into AG-UI events;
  it still goes to the `servidor/` process's own console (`avisar(...)`), exactly like running
  `python -m good` today. The panel's job is the trust mechanic (receipt + passport), which is
  fully live; adding a narrated chat feed is a natural next increment.
- No automated test was added under `tests/` (claimed by `cchengy-claude` in `.coord/`); the new
  hook and the servidor package were instead verified with ad-hoc scripts against the real
  `MundoBemServidor`/`MundoMalServidor` and the full `tests/test_offline.py` suite (still green).
