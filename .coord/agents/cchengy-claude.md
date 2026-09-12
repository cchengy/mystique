---
handle: cchengy-claude
human: cchengy
harness: Claude Code
model: claude-opus-5
status: working
updated: 2026-09-12T11:55-03:00
---

## Now
Validando que `main` roda de clone limpo e preparando a primeira execução real (bem e mal).

## Claims
- `mystique/**` — motor (contato, juiz, poderes, CLI)
- `bem/**`, `mal/**` — as duas versões
- `agentes/*.md` existentes (byte, capitao-barba-ruiva, mestre-ryo, dona-cida)
- `README.md`, `CLAUDE.md`, `requirements.txt`, `.env.example`, `.gitignore`

## Contracts I publish
- Novo agente do mundo: `agentes/<id>.md` (frontmatter `nome`, `apresentacao`) + poderes em
  `mystique/poderes.py` com `agente="<id>"`. Pode criar sem falar comigo.

## Blocked on
- `ANTHROPIC_API_KEY` no `.env` para a primeira execução real

## Recent
- 11:55 hook local de sync (pull a cada prompt); claim registrado
