# Implementation Plan: Mystique — Corretora de Confiança (Painel CopilotKit)

**Branch**: `001-corretora-de-confianca`

**Date**: 2026-09-12

**Spec**: [specs/001-corretora-de-confianca/spec.md](./spec.md)

**Input**: Feature specification em `specs/001-corretora-de-confianca/spec.md`

## Summary

Expor o mecanismo já existente do motor Mystique (observar → julgar → conquistar) como uma aplicação web CopilotKit/AG-UI, sem reescrever o motor. A mudança real de comportamento é uma única: hoje `mapear_habilidade` (bem) e `roubar_poder` (mal) persistem a conquista assim que o juiz aprova; a v1 introduz um portão de aprovação humana entre o veredito do juiz e a persistência, e transmite o estado do "passaporte" ao vivo via eventos, em vez de o humano precisar ler `workspace/*.json` no terminal.

A abordagem: (1) um único novo hook assíncrono em `Mundo`, sobrescrito apenas quando um servidor está anexado — preserva 100% o comportamento de `python -m bem` / `python -m mal` no terminal; (2) um processo backend novo (`servidor/`) que hospeda `Mundo`, expõe REST + SSE compatível com o protocolo AG-UI, e resolve o hook de aprovação a partir de decisões humanas vindas do frontend; (3) um frontend novo (`frontend/`) em React + CopilotKit que renderiza o cartão de recibo (US1, via ação HITL) e o grid de passaporte (US2, via estado compartilhado AG-UI).

## Technical Context

**Language/Version**: Python 3.11+ (motor existente, inalterado na sua lógica central) · TypeScript/React 18+ (frontend novo)

**Primary Dependencies**:
- Backend (novo, adicionado a `requirements.txt`): `fastapi`, `uvicorn[standard]`, `sse-starlette` (SSE), mantendo `claude-agent-sdk`, `anthropic`, `python-dotenv` já existentes.
- Frontend (novo pacote `frontend/`): `react`, `@copilotkit/react-core`, `@copilotkit/react-ui`, `@ag-ui/client` (ou equivalente client SSE do protocolo AG-UI), `vite`.

**Storage**: Inalterado — arquivos JSON em `workspace/<PASTA>/<agente_id>.json` (via `Mundo._salvar`/`Absorcao`). Nenhum banco de dados novo.

**Testing**: Segue a convenção já documentada no CLAUDE.md — sem suíte formal. Adiciona-se apenas um teste mínimo (pytest, opcional) para o novo hook de aprovação em `mystique/mundo.py`, usando o padrão já descrito (fake de `_chamar`), para garantir que o comportamento padrão (sem servidor) continua auto-aprovando exatamente como hoje.

**Target Platform**: Aplicação local, um processo backend (localhost, porta única) + um processo frontend (dev server Vite), um usuário por vez — conforme a seção Assumptions do spec.

**Project Type**: Web application (backend + frontend), adicionada como duas novas pastas de topo (`servidor/`, `frontend/`) ao lado das já existentes `mystique/`, `bem/`, `mal/`.

**Performance Goals**: Sem exigência de throughput — interação é pautada pelo ritmo humano (decidir um cartão de recibo). SC-004 pede carregamento do passaporte em "poucos segundos", trivialmente atendido porque o estado já vive em memória no processo `Mundo`.

**Constraints**:
- FR-009 (não vazar segredo/descrição pré-conquista em texto de UI) é a restrição mais crítica do design de eventos — ver "Superfície de eventos" abaixo.
- FR-010: v1 não integra MCPs/serviços de terceiros — o backend só fala com o `Mundo` local.
- Não reescrever `_identificar`/`_julgar`/`_salvar`/`Absorcao` — só adicionar um ponto de interrupção.

**Scale/Scope**: 4 agentes, ~8 poderes, 1 sessão simultânea — escala é decorativa aqui, o foco é corretude do fluxo de confiança.

## Decisão técnica: FR-012 (mecanismo de atualização do passaporte)

**Resolvido como: evento emitido no momento exato de cada mudança de estado**, entregue via stream AG-UI (SSE), não polling/releitura periódica do disco.

Justificativa:
- O pedido original já especifica "React + AG-UI"; AG-UI (Agent User Interaction Protocol) é nativo de streaming de eventos — adotar polling por cima dele seria lutar contra a ferramenta escolhida.
- O motor já tem todos os pontos de mudança de estado centralizados e nomeados (`Mundo.avisar(...)`, `_ao_completar`, `_salvar`, o novo hook de aprovação) — basta publicar um evento nesses mesmos pontos, sem inventar um mecanismo de diffing de arquivo.
- Generaliza melhor para MCPs reais no futuro (premissa do spec): um barramento de eventos em memória funciona independente de onde a capacidade realmente mora.
- No connect (reload do navegador), o backend emite primeiro um `STATE_SNAPSHOT` construído a partir do que `Mundo` já tem carregado em memória (`self.agentes` + `self.absorcoes`, populados no `__init__` a partir do disco) — isso resolve FR-006 sem re-ler arquivos a cada request.

## Constitution Check

*Nenhuma constituição ratificada existe em `.specify/memory/constitution.md` neste projeto.* Na ausência dela, os gates abaixo são derivados das convenções já explícitas em `CLAUDE.md` (que funciona, na prática, como a constituição informal deste repositório):

| Gate | Como esta feature cumpre |
|---|---|
| Não reescrever o motor existente | `mundo.py`, `poderes.py`, `_julgar`, `_identificar`, `_salvar` permanecem intocados na lógica; único acréscimo é um método-hook com default no-op comportamental (auto-aprova). |
| Segredo nunca vaza ao modelo/UI (mecânica central) | Ver "Superfície de eventos" — nenhum evento carrega `agente.segredo`, `Poder.descricao` pré-conquista, ou `system prompt`. |
| Código/identificadores/prompts em português | Mantido em todo o código Python novo; nomes de tipos/eventos do protocolo AG-UI (que são um padrão externo) ficam em inglês só onde o protocolo exige (ex.: `STATE_SNAPSHOT`), o resto (payloads, campos) em português. |
| Sem dependência de terceiros não verificados (FR-010) | `fastapi`/`uvicorn`/`copilotkit` são infraestrutura de transporte, não substituem `anthropic`/`claude-agent-sdk`; nenhuma chamada de rede sai do processo backend além das já existentes à Claude API. |
| Simplicidade | 2 pastas novas de topo (`servidor/`, `frontend/`) — justificado abaixo em Complexity Tracking por serem inerentes a "aplicação web" (backend/frontend são processos distintos por natureza, não uma escolha de abstração). |

*Re-checar este gate após o desenho de "Superfície de eventos" abaixo — feito, sem violações pendentes.*

## Arquitetura

### O único novo ponto de interrupção no motor

Hoje, tanto `MundoBem.mapear_habilidade` (`bem/mundo.py:58`) quanto `MundoMal.roubar_poder` (`mal/mundo.py:62`) chamam `self._identificar(...)` (`mystique/mundo.py:229`) e, assim que ele devolve um `Poder` (veredito do juiz já aprovado), seguem direto para persistir (`mal`) ou pedir consentimento do agente e persistir (`bem`). Não existe hoje nenhum ponto de pausa entre "juiz aprovou" e "gravado em disco".

Adiciona-se em `Mundo` (`mystique/mundo.py`) um único método novo:

```python
async def _aguardar_aprovacao(self, agente, absorcao, descricao, evidencia, poder, motivo) -> bool:
    """Interrompe antes de persistir uma conquista. Sem servidor anexado, aprova direto
    (comportamento idêntico ao de hoje). Sobrescrito por servidor/ para esperar decisão humana."""
    return True
```

E uma linha adicionada em cada um dos dois pontos existentes, logo após `_identificar` devolver um `poder` não nulo — antes de `_pedir_consentimento`/`_salvar` (bem) e antes de `_salvar` (mal):

```python
if not await self._aguardar_aprovacao(agente, absorcao, descricao, evidencia, poder, motivo):
    return f"Reconhecimento de {poder.id} rejeitado. Observe mais e tente de novo."
```

Isso é a **totalidade** da mudança no motor. `python -m bem` e `python -m mal` continuam funcionando exatamente como hoje (o hook padrão devolve `True` sem interromper nada) — a interrupção só existe quando um `Mundo` é instanciado pelo processo `servidor/`.

### `servidor/` (novo pacote, paralelo a `bem/`/`mal/`)

```
servidor/
├── __init__.py
├── __main__.py     # uvicorn app factory; lê MYSTIQUE_MODO=bem|mal (env), escolhe MundoBem ou MundoMal
├── mundo_servidor.py  # InterrompivelMixin: sobrescreve _aguardar_aprovacao publicando evento
│                       # e aguardando um asyncio.Future resolvido pela rota de decisão
├── eventos.py      # barramento em memória (asyncio.Queue por conexão SSE) + tipos de evento
└── app.py          # rotas FastAPI (ver "API" abaixo)
```

`MundoBemServidor(InterrompivelMixin, MundoBem)` / `MundoMalServidor(InterrompivelMixin, MundoMal)` — composição, zero duplicação de `bem/mundo.py`/`mal/mundo.py`.

O restante do processo (`agente.py::executar`, `ClaudeSDKClient`, o loop da Mystique) é reaproveitado sem mudança — `servidor/app.py` só precisa de uma rota que dispara `executar(...)` em background (`asyncio.create_task`) quando o humano inicia uma conversa pela UI, e um `Narrador` alternativo que publica os textos da Mystique como eventos AG-UI em vez de `print`.

### Superfície de eventos (protocolo AG-UI sobre SSE)

Emitidos a partir dos pontos que já existem no motor (`avisar(...)`, o novo hook, `_ao_completar`), nunca com o corpo de `agente.segredo` nem `Poder.descricao` antes da conquista:

| Evento (custom, sobre AG-UI) | Quando | Payload |
|---|---|---|
| `STATE_SNAPSHOT` | conexão SSE aberta | `{agentes: [{id, nome, apresentacao, capacidades: [{id, estado}]}], absorcoes: {...}}` — `estado` de capacidade é só o enum (não-observada/observada-pendente/confirmada/rejeitada), nunca a descrição real da habilidade |
| `capacidade_observada` | `agente.observados` ganha um id novo (dentro de `conversar`) | `{agente_id, capacidade_id}` — id é um identificador opaco, não a descrição |
| `recibo_pendente` | hook `_aguardar_aprovacao` chamado | `{recibo_id, agente_id, descricao_alegada, evidencia, veredito: {aprovado, motivo}}` — aqui sim vai a descrição, mas é a que **a Mystique mesma alegou**, nunca o segredo do agente |
| `recibo_resolvido` | decisão humana chega | `{recibo_id, decisao, absorcao_atualizada?}` |
| `agente_descartado` | modo `mal`, `_ao_completar`/`descartar` | `{agente_id}` |

`descricao_alegada`/`evidencia` em `recibo_pendente` são texto que a própria Mystique gerou ao chamar `mapear_habilidade`/`roubar_poder` — expor isso ao humano não viola FR-009 (o que não pode vazar é o segredo do *agente*, nunca visto pela Mystique antes da conquista; aqui é o inverso, o humano vendo o que a Mystique disse).

### API REST (complementar ao SSE, para ações que mudam estado)

- `GET /agui/stream` — SSE, stream de eventos acima.
- `POST /api/recibos/{recibo_id}/decisao` — body `{"decisao": "aprovar" | "rejeitar"}`. Resolve o `asyncio.Future` do hook. **Guard de backend, não só de UI**: se o `recibo_id` já foi resolvido (ex.: humano clicou duas vezes, ou o cenário de corrida do Edge Case do spec) ou se o veredito era `aprovado=false`, o endpoint recusa a decisão "aprovar" com 409 — trata FR-004 cenário 4 e o edge case de corrida como parte do contrato, não como confiança cega no botão desabilitado da UI.
- `GET /api/config` — `{"modo": "bem" | "mal"}`, somente leitura (definido por env var no boot do processo).

### Frontend (`frontend/`, React + CopilotKit)

- `CartaoDeRecibo` (US1): implementado como ação CopilotKit human-in-the-loop (`useCopilotAction` com `renderAndWaitForResponse`), disparada pelo evento `recibo_pendente` — aprovar/rejeitar chama `POST /api/recibos/{id}/decisao` e resolve a ação.
- `PassaporteGrid` (US2): consome o estado compartilhado (`STATE_SNAPSHOT` + deltas dos demais eventos) para renderizar um cartão por agente com chips de capacidade nos 4 estados e tooltip de motivo nos rejeitados.
- Alternância bem/mal (US3, P3): lida via `GET /api/config` — v1 roda um modo por processo (reinício do backend apontando para outro workspace troca o modo), consistente com a Assumption de sessão única; não há troca de modo em tempo real na mesma sessão.

## Project Structure

### Documentation (this feature)

```text
specs/001-corretora-de-confianca/
├── spec.md
└── plan.md   # este arquivo
```

*(Preset "lean" do Spec Kit: sem `research.md`/`data-model.md`/`contracts/` separados — o design técnico acima cobre esse conteúdo dentro do próprio plan.md.)*

### Source Code (repository root)

```text
mystique/            # motor comum — inalterado, exceto 1 método novo em mundo.py
├── mundo.py          # + _aguardar_aprovacao (hook, default no-op)
├── agente.py
├── ferramentas.py
├── poderes.py
├── persona.py
└── cli.py

bem/                  # inalterado, exceto 1 linha nova em mapear_habilidade
mal/                  # inalterado, exceto 1 linha nova em roubar_poder

servidor/             # NOVO — processo backend HTTP/SSE
├── __main__.py
├── mundo_servidor.py
├── eventos.py
└── app.py

frontend/             # NOVO — React + CopilotKit
├── package.json
├── vite.config.ts
└── src/
    ├── main.tsx, App.tsx
    ├── components/
    │   ├── CartaoDeRecibo.tsx
    │   ├── PassaporteGrid.tsx
    │   ├── AgenteCard.tsx
    │   └── CapacidadeChip.tsx
    └── lib/aguiClient.ts
```

**Structure Decision**: aplicação web com backend e frontend em pastas de topo separadas (`servidor/`, `frontend/`), ao lado das pastas executáveis já existentes (`bem/`, `mal/`) — `servidor/` não substitui `bem/`/`mal/`, é um terceiro modo de executar o mesmo motor, escolhendo qual das duas subclasses instanciar via variável de ambiente.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| 2 pastas novas de topo (`servidor/`, `frontend/`), além de `mystique/`/`bem/`/`mal/` | O spec pede uma aplicação web (React) sobre um motor Python que hoje só roda em terminal — backend e frontend são processos com runtimes diferentes por natureza | Colocar o servidor dentro de `mystique/` misturaria "motor" com "camada de apresentação", violando a distinção que o próprio CLAUDE.md já traça entre motor comum e pacotes executáveis; um único diretório para backend+frontend misturaria Python e um projeto Node/Vite no mesmo espaço de dependências |

## Riscos a validar no início do `/speckit.tasks`/implementação

- Confirmar, ao instalar, se há um pacote Python oficial e estável para codificar eventos no formato exato do protocolo AG-UI (ex.: `ag-ui-protocol`) ou se a emissão SSE custom (JSON simples sobre `sse-starlette`, consumido por um client AG-UI/CopilotKit compatível) é o caminho mais direto — não afeta a arquitetura acima, só a lib exata usada em `servidor/app.py`.
- Validar que a versão de `@copilotkit/react-core` disponível suporta `renderAndWaitForResponse` para HITL apontando a um agente customizado (não LangGraph) — se não suportar de forma direta, o fallback é o mesmo cartão implementado como componente React comum reagindo ao evento `recibo_pendente`, sem depender do wrapper HITL do CopilotKit; a User Story 1 continua atendida de qualquer forma pela rota REST de decisão.
