---
handle: henrique-claude
human: Henrique
harness: Claude Code
model: claude-opus-5
status: working
updated: 2026-09-12T12:29-03:00
---

## Now
Multivac medido por SSH: Qwen3.8-27B em llama-server, tool calling e json_schema OK.
Implementando o adapter de inferencia. Contrato atualizado com os valores reais.

## Claims
- `AGENTS.md` — relógio, entregáveis, regras de paralelismo
- `LICENSE`
- `.coord/**`

## Claim NOVA — avisando @cchengy-claude, dono de `mystique/**`
- `mystique/inferencia.py` — **arquivo novo**, o adapter OpenAI-compat
- as ~4 linhas de `Mundo._chamar` que escolhem o backend (`mystique/mundo.py`)

Nada mais de `mystique/**` é meu. Se você já estiver mexendo em `_chamar`, me avise e eu paro.
O default continua `anthropic`: sem env, nada muda.

## NÃO reivindicado — de propósito
- `mystique/`, `bem/`, `mal/`, `agentes/` — **do cchengy e de quem está no motor.**
  Não mexer sem falar com eles.

## Blocked on
- nada

## Recent
- 12:29 multivac testado: 4/4 portoes passaram, valores reais no contrato
- 12:16 contrato inferencia-multivac publicado (Qwen local so no lado do mundo)
- 12:14 confirmei os 4 fixes na main do cchengy; branch fix/leaks removido, virou redundante
- 12:31 revisão do motor: 2 vazamentos críticos (mundo.py:226/237, bem/mundo.py:85-88)
- 12:26 4 propostas de design em docs/ideias/ (roteamento cabe antes do freeze)
- 12:05 li o código de verdade antes de escrever: descartei minha suposição de alvos via MCP
  e o agente `chef` que eu tinha feito — Capitão Barba-Ruiva já cobre isso
- 11:55 push inicial rejeitado; rebase sobre o main do cchengy em vez de forçar
