# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Mandatory: read [`AGENTS.md`](AGENTS.md) before doing any work, every session.** It holds the
> hackathon's hard rules, the clock, the deliverables and who owns which files. This file explains
> how the code works; `AGENTS.md` explains how the team works, and its hard rules override anything
> here. Re-read it after every sync, because teammates update it during the day.

## Project

Mystique: an autonomous agent (hackathon, Python) inspired by the X-Men character. She is born with only metamorphosis, talks to the agents of a "world", and deduces each one's personality and abilities purely from their answers. There are two versions:

- `good/`: builds an adapter per agent (interaction protocol plus abilities connected with consent). The agent keeps its abilities.
- `evil/`: steals the powers. The agent loses them and is discarded.

**Language:** everything visible (docs, prompts, agent personas, terminal output, tool and power descriptions, docstrings) is in English, and so are the version folders (`good/`, `evil/`, matching `Mundo.modo`). Other identifiers stay in Portuguese: modules, classes, functions, tool names and JSON field names (`agentes/`, `poderes.py`, `MundoBem`, `conversar`, `descricao`...).

Team files owned by others: `AGENTS.md` (hackathon rules and clock), `.coord/` and `docs/`. Read `AGENTS.md`, and only edit your own `.coord/agents/<handle>.md`.

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env                               # ANTHROPIC_API_KEY
.venv/bin/python -m good                           # interactive
.venv/bin/python -m evil "mission" --budget 2 -v   # single run
.venv/bin/python tests/test_offline.py             # offline test, no key needed
cd web && npm install && npm run dev               # React replay of both points of view (no key)
cd web && npm run build                            # type-check + build the replay
```

`web/` (Vite + React + TypeScript) is a scripted replay for the demo video and is not wired to the Python engine. `web/src/scenario.ts` copies engine strings verbatim (tool results, notices, narration), so when an engine message changes, update the scenario too.

No lint is configured. `tests/test_offline.py` is a plain script (no pytest). It swaps `Mundo._chamar` for a fake async function that returns objects with `stop_reason` and `content`. The `_json` calls (judge and consent) also go through it. Every real run spends API credits: Mystique plus every agent, judge and consent call.

## Architecture

`mystique/` is the shared engine. `good/` and `evil/` are runnable packages that hand three things to `mystique.cli.main`: a `Mundo` subclass, a persona, and a function that returns the extra tools.

Model paths are provider-agnostic. With no provider env vars set, everything runs on Claude:

- **Mystique** runs on the Claude Agent SDK by default (`ClaudeSDKClient` in `mystique/agente.py`, bundled CLI included). With `tools=[]` she gets no built-in tools, only the in-process MCP server `mundo`: the base tools from `mystique/ferramentas.py` plus the version's extras. With `MYSTIQUE_PROVIDER=openai`, `mystique/agente_local.py` runs her loop against any OpenAI-compatible server instead. It reuses the same `SdkMcpTool` objects, so the game rules exist in one place only.
- **World agents**, the judge and consent all go through `Mundo._chamar`, the single choke point. By default that is the Claude API (`anthropic.AsyncAnthropic`). With `MYSTIQUE_WORLD_PROVIDER=openai`, `mystique/inferencia.py` translates to an OpenAI-compatible server and returns Anthropic-shaped objects, so `conversar`, `_json` and the offline test stay unchanged. The body of `agentes/<id>.md` becomes the agent's system prompt, and the powers in `mystique/poderes.py` become its tools, run in a manual loop in `Mundo.conversar`.

| Mystique | World | Needs |
|---|---|---|
| Agent SDK | Claude API | `ANTHROPIC_API_KEY` (default) |
| Agent SDK | self-hosted | key + server |
| self-hosted | self-hosted | no vendor key (verified live by the team) |
| self-hosted | Claude API | key |

The CLI only asks for a Claude key on paths that call Anthropic. Variables: `MYSTIQUE_PROVIDER`, `MYSTIQUE_BASE_URL` and `MYSTIQUE_MODEL_ID` for Mystique (falling back to the world's), and `MYSTIQUE_WORLD_PROVIDER`, `MYSTIQUE_WORLD_BASE_URL`, `MYSTIQUE_WORLD_MODEL` and `MYSTIQUE_WORLD_API_KEY` for the world. Self-hosted runs are slower (about 50s for a tool-chaining conversation, 20s for the judge).

The core mechanic is the secret:

- Mystique never sees an agent's prompt, or the names and descriptions of its abilities, before earning them. `conversar` only tells her *that* the agent used an ability.
- An ability can only be earned after it has been observed (`Agente.observados`), and `_julgar` validates her description against the real one.
- Do not leak this data in text returned to the model. `avisar(...)` output only reaches the terminal, so it is safe there.

State:

- State lives in Python and is shared with the tools through closures.
- `Absorcao` is persisted to `<version>/workspace/<PASTA>/<id>.json` and re-applied on load by `_ao_carregar` (in `evil/`, theft and discard are permanent).
- Subclasses customize through hooks: `total`/`feitos` (progress), `_indisponivel`, `_ao_completar`, `_system_agente`, `resumo`, `descrever`.
- The active form is re-injected every turn by `Mundo.envelopar` as `<active_form>`, with intensity proportional to progress.

Gotchas:

- `permission_mode="dontAsk"`: only the tools in `nomes_permitidos` (`mcp__mundo__<name>`) run. A new tool must be in the list the version returns.
- `setting_sources=[]` keeps Mystique from inheriting settings, hooks or this CLAUDE.md.
- Powers run real code: `executar_python` runs a subprocess with a 10s timeout in a temporary directory. `AGENTS.md` says not to widen it.
- `poderes.MUNDO_REAL` lists powers that reach outside the simulation (the Archivist's Exa search). `evil/` refuses to steal them. Add any new real-world power to that set.
- `mystique/auditoria.py`: the `auditar_agente` tool writes a security and LGPD audit (RIPD-style, citing LGPD articles) to `<version>/workspace/auditorias/<id>.md`. It needs prior contact. In `good/`, `mapear_habilidade` requires an audit and refuses when the audit rates the agent high risk. The report may only contain what Mystique knows: never add the names or descriptions of abilities she has not earned. Mystique asks agents about their data practices and never probes them adversarially.
- The frontmatter of `agentes/*.md` is read by a minimal non-YAML parser: only single-line `key: value` entries (`nome`, `apresentacao`, and for external agents `url`, `modelo`, `chave_env`).
- External agents (`url:` in the frontmatter) are real agents reached through `inferencia.ClienteOpenAI`, one client per agent in `Mundo._externos`. `chave_env` names the env var holding the key; never put a key in the file. Only versions with `aceita_externos = True` (good) may reach them. The gate is in `Mundo._agente`, which every action goes through, so do not add an action that looks agents up without it. `evil/` must never reach an external agent (`AGENTS.md`: nothing points to third-party systems).

## Conventions

- Models via env: `MYSTIQUE_MODEL` and `MYSTIQUE_AGENTS_MODEL` (default `claude-opus-5`).
- Direct calls use `client.beta.messages.create` with `fallbacks="default"`, the `server-side-fallback-2026-07-01` beta, and handle `stop_reason == "refusal"`.
- Structured output uses `output_config.format` with a `json_schema`; the judge returns `ability`/`reason`, consent returns `allows`/`reply`.

---

## ⛔ REGRA DE BRANCH — vale só para este repositório

**A branch `main` está congelada no estado da submissão do hackathon (`643104d`, 12/09/2026 16:00 -03).**

Os organizadores do AI Tinkerers vão olhar a `main`. Qualquer commit nela com data posterior
ao deadline pode **desclassificar o time**.

**Todo trabalho a partir de agora vai para a branch `post-hackathon`.**

```bash
git checkout post-hackathon        # antes de qualquer edição
git push origin post-hackathon     # nunca `git push origin main`
```

- **Nunca** commite nem empurre para `main` neste repositório sem o Henrique pedir
  explicitamente, nem mesmo documentação: um commit de doc também carrega data.
- Antes de empurrar, confira: `git rev-parse --abbrev-ref HEAD` precisa dizer `post-hackathon`.
- `post-hackathon` contém todo o histórico, inclusive os commits pós-deadline que saíram da
  `main`. Nada foi perdido.

### Feature dependency map and commit discipline

Every feature-changing commit updates this table. UI-contract changes update `DESIGN.md` in
the same commit. Do not merge a feature whose dependency record is stale.

| Feature | Source of truth | Depends on | Downstream surfaces |
|---|---|---|---|
| 24-hour credential broker | `cofre/` + private volume | Auth0 JWT, AES-256-GCM master key, isolated networks, `vault-init` chown of the volume | all BYOK providers |
| Live conversation | `servidor/sessoes.py` account records | Auth0 `sub`, active broker credential | rail, transcript, mission |
| Main-model context | selected session messages | per-account session store | next completion |
| Good/Evil profile | session `modo`, isolated world workspace | persona/tools, account event bus | live run, Compare |
| Reasoning evidence | per-account workspace + session projection | judge outcome and recall | session, Compare |
| Reasoning Bank recall | `mystique/banco.py` per account+profile workspace | failed verdict, agent id | the tool result Mystique reads — never the judge's input |
| Interface language | user choice in `localStorage`, `web/src/pt.ts` | English source strings | every visible string, and the mission's answer language |
| Exa retrieval | user BYOK in credential broker | mission-scoped broker token, Good real-world policy | sourced answers; Evil blocks it |
| Model selection | user OpenRouter BYOK + saved model id | credential broker proxy | model drawer, missions |
| Guided Replay | `web/src/scenario.ts` | recorded scenario only | replay, never live evidence |
| Account lifecycle | `auth_time`/`iat` + `delete_after` | Auth0 login, in-process purge, task/cache eviction | onboarding, settings, deletion |
| Live transport | authenticated fetch/SSE | Auth0 access token, account event bus | synchronization |

### Isolated 24-hour BYOK: non-negotiable

[`docs/decisoes/02-cofre-byok-24h.md`](docs/decisoes/02-cofre-byok-24h.md) is the security
authority. Auth0 authenticates; it does not encrypt or recover application data. Every
provider is BYOK. Only `credential-broker` may mount the credential volume or receive
`MYSTIQUE_VAULT_KEY`; the main application must use its authenticated internal proxies.

Provider credentials expire exactly 24 hours after connection, without sliding renewal.
Sessions and all other account information expire after 60 days without a successful
login. Both rules must be explicit in onboarding and settings. Never describe this
standard-VPS design as zero-knowledge or protected against root/Docker/operator access.
Never add a server-wide provider-key fallback for authenticated users.
Production must set `MYSTIQUE_REQUIRE_AUTH=true` and fail at startup if Auth0 is incomplete.
Provider proxies stay on an explicit endpoint/method allowlist. Account deletion and expiry
must cancel active missions and evict worlds, clients, bearers and event buses before disk data.

The Reasoning Bank is the learning loop: recall goes to Mystique, in her own words, and
never into the judge's evidence — the judge knows the answer key. See
[`docs/auditorias/2026-09-13-learning-and-accounts.md`](docs/auditorias/2026-09-13-learning-and-accounts.md)
for the audit of that chain, what was fixed and what is still open.

Every visible string is English in the source and translated through `web/src/pt.ts`.
Never inline Portuguese in a component: the other language would have nothing to fall
back to. `npm test` fails on inline accented text.

Before commit: update this map if dependencies changed; update `DESIGN.md` for UI changes;
run offline/backend tests, `npm test`, `npm run build`; inspect light/dark and desktop/mobile.
