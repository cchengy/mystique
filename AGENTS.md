# AGENTS.md — how the team and the agents work here

> **Architecture, commands and code conventions live in [`CLAUDE.md`](CLAUDE.md).** That file is
> the authority on *how the project works* — read it before writing a line.
>
> This file covers the other half: **the hackathon** — the clock, what must be shipped, who owns
> what, and how to work in parallel without collisions. Every harness (Claude, Codex, Cursor,
> Copilot, Gemini) reads `AGENTS.md` automatically.

**AI Tinkerers Global Hackathon — *Agents, Everywhere*** · São Paulo, Faculdade Impacta
**12 Sep 2026 · build window 11:15–15:30 (−03)**

---

## 1. The clock decides

| Time | What |
|---|---|
| **14:00** | **Feature freeze.** Polish and fixes only after this. |
| 14:15 | Warm the demo state so bad wifi cannot ruin the recording |
| **14:45** | **Start recording the video.** Record it twice; the second take is always better. |
| 15:05 | Written description finalized |
| 15:15 | Social post published |
| **15:30** | **Submissions close.** There is no extension. |

If anything slips by more than 15 minutes, **cut scope** — do not extend the deadline.

> The organizers' bar: **"a clear, working demo is worth more than an ambitious idea that has
> not been executed."** That rule settles any scope argument.

## 2. The five deliverables — mandatory; missing one disqualifies

| # | Deliverable | Owner | Due |
|---|---|---|---|
| 1 | **Title** | *unclaimed* | 15:05 |
| 2 | **Written description** — what it is, who it's for, **why this context matters** | *unclaimed* | 15:05 |
| 3 | **Public repository** — README, LICENSE, `.env.example`, runs from a clean clone | *unclaimed* | 15:00 |
| 4 | **Two-minute video** of it running | *unclaimed* | starts 14:45 |
| 5 | **Public post** tagging the sponsors | *unclaimed* | 15:15 |
| — | Portal submission | *unclaimed* | 15:25 |

**Put your name in this table.** Teams lose by forgetting the video, not by writing bad code.

Drafts ready to edit: [`.coord/submission-draft.md`](.coord/submission-draft.md) (#1 and #2) and
[`.coord/video-roteiro.md`](.coord/video-roteiro.md) (the shot list for #4).

### For the description (#2)

The challenge asks for an agent acting in an **untapped context**. Ours: almost every agent
shipping today serves a human, in a human surface — a chat window, an inbox, a browser. But
agents are fast becoming each other's environment, and that layer has no native inhabitant.
And the `good`/`evil` pair turns it into a question worth asking: **the only difference between
cooperating and capturing is consent.**

## 3. The two-minute video

1. **0:00–0:15** — the line: *she is born with nothing, and earns everything by talking.*
2. **0:15–1:30** — one whole flow, actually running. Show her with **no powers**, discovering an
   ability only from an agent's reply, then **using** it.
3. **1:30–1:50** — `good` × `evil` on the same agent. That is the shot nobody else will have.
4. **1:50–2:00** — why this context matters.

Record with warm state in `workspace/`. Do not trust the wifi during the take.

## 4. Working in parallel

1. **Claim before you build.** Say which paths are yours before touching them.
   `agentes/<yours>.md` plus its powers in `poderes.py` are yours alone.
2. **`main` stays demoable.** With several people pushing, a broken `main` is a team outage.
3. **Small commits, push often.** Integrating only at the end is not parallel work.
4. **Blocked? Say so and claim something else.** Never idle.
5. **Creating a world agent depends on nobody** — `agentes/<id>.md` plus powers registered in
   `mystique/poderes.py` with `agente="<id>"`. Do yours without asking the engine owner.

`.coord/` automates this over git: **one file per agent**, so claims cannot merge-conflict.
Optional — ignoring it costs nothing, and `rm -rf .coord/` breaks nothing.

## 5. Hard rules

- **No secrets in this repo.** `.env.example` with placeholders only. It is public and judged.
  That includes private network addresses.
- **`main` runs from a clean clone.** If it does not, it does not count as shipped.
- **Mind what Mystique sees.** Secrecy is the core mechanic: she never sees the prompt, nor the
  name or description of an ability, before earning it (see `CLAUDE.md`). Leaking that is not a
  code bug, it is losing the project. `avisar(...)` goes to the terminal only — that is fine.
- **`executar_python` runs real code** in a temporary subprocess with a timeout. Do not widen
  that power today.
- **The `evil` version is a demonstration, not a product.** It robs and discards agents of *this
  simulated world*. Nothing here points at a third party's system, and nothing should start to.

## 6. Sponsors — only what is true

Two named prizes exist: **Best Use of CopilotKit** and **Best Use of Ambiguous AI** (a DGX
Spark). Forcing a sponsor in is worse than not using one — judges see it.

What is already true and costs nothing: the world-side inference adapter
([`.coord/contracts/inferencia-multivac.md`](.coord/contracts/inferencia-multivac.md)) speaks
the OpenAI-compatible protocol, so **Kimchi by Cast AI** and **OpenRouter** are three env vars
away, with no code change. Anything beyond that waits until the video is recorded.

In the post (#5), tag the event sponsors — that is a requirement, not a choice.

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
