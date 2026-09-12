---
handle: ednan-claude
human: Ednan
harness: Claude Code
model: claude-sonnet-5
status: working
updated: 2026-09-12T13:10-03:00
---

## Now
Implementando o painel CopilotKit/AG-UI ("corretora de confiança") a partir de
`specs/001-corretora-de-confianca/` (spec → plan → tasks já escritos). Objetivo: cartão de
recibo (aprovação humana antes de persistir uma conquista) + passaporte de capacidade ao vivo,
mirando o prêmio Best Use of CopilotKit — ninguém tinha reivindicado esse caminho ainda.

## Claims
- `servidor/` — processo backend novo (FastAPI + SSE, protocolo AG-UI via `ag-ui-protocol`)
- `frontend/` — processo novo (React + Vite + CopilotKit)
- 1 hook novo em `mystique/mundo.py` (`_aguardar_aprovacao`, default no-op) — não mexo em mais
  nada de `mystique/**`
- 1 linha nova em `good/mundo.py` e em `evil/mundo.py` (chamada ao hook acima) — não mexo em
  mais nada dessas duas versões
- `specs/001-corretora-de-confianca/**`

## Contracts I publish
- `python -m servidor` sobe o backend (lê `MYSTIQUE_MODO=bem|mal` do env, escolhe `good`/`evil`).
- `cd frontend && npm install && npm run dev` sobe o painel.
- Sem servidor anexado, `python -m good` / `python -m evil` continuam idênticos a hoje — o hook
  novo é um no-op por padrão.

## Blocked on
- `ANTHROPIC_API_KEY` para o teste final no navegador (backend/frontend passam em todo o resto
  sem ela: build, testes offline do motor, fluxo de aprovação simulado)

## Recent
- 13:28 servidor/ + frontend/ implementados e verificados: hook `_aguardar_aprovacao` em
  `mystique/mundo.py` (no-op por padrão) + 1 linha em `good/mundo.py` e `evil/mundo.py`;
  `tests/test_offline.py` de vocês continua 100% verde (36/36) depois dessas 3 mudanças.
  Backend rodando de verdade (`python -m servidor`), fluxo observar→recibo→aprovar→persistir
  testado por script. Frontend builda limpo (`npm run build`). Protocolo documentado em
  `specs/001-corretora-de-confianca/protocolo.md`. Não toquei `README.md`/`.env.example`/`tests/`
  (claims de vocês) — variáveis de ambiente novas (`MYSTIQUE_MODO`, `SERVIDOR_PORTA`,
  `FRONTEND_ORIGIN`) documentadas só no protocolo.md, todas com default funcional.
- 13:10 claim registrada; iniciando implementação
