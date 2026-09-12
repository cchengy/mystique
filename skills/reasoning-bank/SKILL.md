---
name: reasoning-bank
description: >-
  Keep a durable, traceable memory of what an agent tried, whether it worked, and why — so the
  next attempt starts from evidence instead of repeating a failed guess. Records one reasoning
  trace per attempt with an outcome, the belief that was tested, the evidence, a confidence and a
  usage count; recalls the relevant traces before the next attempt; and rebuilds a human-readable
  wiki so a person can audit what the agent learned, from whom, and whether it held up. Use when
  an agent repeats mistakes across runs, when you need traceability of what it learned, when
  building self-improving or observability layers, or when asked about reasoning banks, agent
  memory, learning from failure, or experience replay. Schema is Istara's ReasoningBank, so
  traces are portable.
license: MIT
compatibility: Needs only a filesystem the agent can read and write. No services, no database, no dependencies.
metadata:
  version: "1.0.0"
  schema: istara.reasoningbank.v1
---

# Reasoning Bank

Most agents throw away their failures. That is the half worth keeping: a failed attempt says
exactly what *not* to try again, and it is the only record of how the agent actually reasons.

| Need | Read |
|---|---|
| Field-by-field schema and file layout | [references/schema.md](references/schema.md) |

## 1. The loop

```
recall ──▶ attempt ──▶ judge ──▶ record ──▶ (wiki rebuilt)
   ▲                                 │
   └─────────────────────────────────┘
```

1. **Recall before acting.** Fetch the traces for this target. Put the **failures first** — they
   are what stops a repeat.
2. **Attempt**, stating the belief you are testing in one sentence.
3. **Judge** the attempt against reality, not against your own confidence.
4. **Record both outcomes.** A success without its matching failures is a story, not a record.
5. The wiki is rebuilt on every write, so a human can audit without reading JSON.

## 2. One trace

Required: `id` · `agent_id` · `source_kind` · `outcome` (`success`|`failure`) · `title` ·
`description` (the belief tested, **in the agent's own words**) · `content` (why it went that
way — the evidence) · `created_at`.

Also carried: `tags` · `domain` · `evidence_refs` · `judge_score` · `confidence` ·
`status` · `usage_count`.

One JSON file per trace, plus `WIKI.md` rebuilt from all of them.

## 3. The rule that matters most

> **Recall must never return anything the agent is not allowed to know.**

A trace has two audiences. `description` is the agent's own words and is safe to read back.
`content` is the judge's reasoning — and a judge usually knows the answer. **Feeding `content`
back into the agent's context can hand it the answer it was supposed to work out.**

So: **recall returns `description` and `outcome`; `content` stays on disk for the wiki and for
humans.** If your judge has no privileged knowledge, this does not apply — but decide it
deliberately, because it is silent when you get it wrong and it invalidates every result after.

## 4. Writing a trace that is worth recalling

- **Describe the belief, not the action.** "I thought he was improvising from memory" beats
  "tried to map ability".
- **Record the failure before you know the answer.** Written afterwards, it is rationalisation.
- **One attempt, one trace.** Do not merge a session into a single entry; the sequence is the data.
- **Let `confidence` be honest.** A confident failure is the most useful entry in the bank.
- **Count reuse.** `usage_count` is how you learn which memories actually earn their place; ones
  never recalled are noise you can expire.

## 5. When not to use it

Single-shot tasks with no second attempt gain nothing. A bank pays off when the same agent meets
the same target more than once, or when a human has to answer *"why does it believe that?"*

## 6. Observability

`summary` gives total, counts by outcome, counts by source kind, and the most-reused trace.
Rising failures on one target means the approach is wrong, not that the agent is unlucky —
that distinction is the reason to keep the bank at all.
