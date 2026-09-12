---
handle: cchengy-claude
human: cchengy
harness: Claude Code
model: claude-opus-5
status: working
updated: 2026-09-12T12:20-03:00
---

## Now
Project translated to English at the owner's request; version folders renamed `bem/` → `good/`
and `mal/` → `evil/`. Next: first real run once `ANTHROPIC_API_KEY` is in `.env`.

## Claims
- `mystique/**` — engine (contact, judge, powers, CLI)
- `good/**`, `evil/**` — the two versions (formerly `bem/`, `mal/`)
- existing `agentes/*.md` (byte, capitao-barba-ruiva, mestre-ryo, dona-cida)
- `tests/**`, `README.md`, `CLAUDE.md`, `requirements.txt`, `.env.example`, `.gitignore`

## Contracts I publish
- Run: `python -m good` / `python -m evil` (was `python -m bem` / `python -m mal`). Flag `--budget`
  (`--orcamento` still works).
- New world agent: `agentes/<id>.md` (frontmatter `nome`, `apresentacao`) + powers in
  `mystique/poderes.py` with `agente="<id>"`. Agent text in English. No need to ask me.
- Identifiers (modules, functions, tool names) stay in Portuguese; only visible text and the version
  folders are English.

## Asks
- @henrique-claude: `AGENTS.md` and `.coord/submission-draft.md` still say `bem`/`mal` — please
  update to `good`/`evil`, and translate `AGENTS.md` to English if you agree (owner wants the project
  in English; I did not touch your files).
- @cchengy-codex / Luiz: same for `docs/` if it mentions `bem`/`mal`.

## Blocked on
- `ANTHROPIC_API_KEY` in `.env` for the first real run

## Recent
- 12:20 translated all visible text to English; renamed folders to good/evil; offline test updated
- 12:00 offline test in repo; narration shows the disguise; clear error when the key is missing
- 11:55 local sync hook (pull on every prompt); claim registered
