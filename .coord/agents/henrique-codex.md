---
handle: henrique-codex
human: Henrique
harness: Codex
model: GPT-5
status: working
updated: 2026-09-12T14:47:00-03:00
---

## Now
Implementing owner-requested capability-aware routing. Every mission must rank the available
agents first, and Reasoning Bank routing outcomes must improve later rankings. Also improving
Cheng's existing web UI in place for WCAG 2.1, interaction heuristics and restrained motion.

## Claims
- `mystique/roteamento.py` — capability catalog and adaptive ranker
- `mystique/mundo.py` — minimal routing lifecycle integration
- `mystique/ferramentas.py` — capability map/routing tools
- `mystique/persona.py` — route-before-contact invariant
- `tests/test_offline.py` — routing and learning regressions
- `web/**` — owner-requested WCAG 2.1 and interaction/motion improvements to Cheng's existing UI

## Contracts I publish
- `Mundo.rotear_tarefa(task)` returns a ranked, human-readable recommendation and stores the
  route context for the next contact.
- Reasoning Bank entries with `source_kind=roteamento` and success/failure outcomes affect future
  rankings; failures are retained rather than discarded.

## Blocked on
- nothing

## Recent
- 14:44 took over the listed engine/test paths from stale `cchengy-claude` claim (updated 12:40),
  limited to the owner-requested router; no UI or deployment paths are touched.
- 14:47 owner expanded scope to `web/**`; took over that stale claim from `cchengy-claude`,
  preserving the existing UI and behavior rather than replacing it.
