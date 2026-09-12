# Tasks: Mystique — Corretora de Confiança (Painel CopilotKit)

**Input**: Design documents from `specs/001-corretora-de-confianca/` (plan.md, spec.md)

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md)

**Tests**: Sem suíte formal (convenção do CLAUDE.md). Inclui-se apenas o teste mínimo já previsto no plan.md para o hook novo do motor — nada além disso é adicionado por padrão.

**Organization**: Tasks agrupadas por fase e, a partir da Fase 3, por user story (US1/US2/US3), para permitir entrega incremental (US1 sozinha já é um MVP demonstrável).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência entre si)
- **[Story]**: a qual user story a task pertence (US1/US2/US3)
- Caminhos de arquivo são exatos, relativos à raiz do repo

---

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Adicionar `fastapi`, `uvicorn[standard]` e `ag-ui-protocol` a [requirements.txt](../../requirements.txt) — trocou `sse-starlette` por `ag-ui-protocol` (ver T002): o encoder da própria lib + `StreamingResponse` do FastAPI já cobrem o SSE, sem infra extra
- [x] T002 [P] Investigado: `ag-ui-protocol` existe no PyPI, é mantido, tem `EventEncoder`/`ag_ui.core` (CustomEvent, StateSnapshotEvent, ...) prontos para Pydantic + SSE — usado de verdade em `servidor/eventos.py`, não um SSE custom
- [x] T003 [P] Pacote `frontend/` criado (Vite + React 18 + TS): `package.json`, `vite.config.ts`, `tsconfig.json`, `index.html` — build (`npm run build`) verificado sem erros
- [x] T004 [P] Decisão tomada com base na pesquisa: **não** adicionar `@copilotkit/react-core`/`react-ui` nesta passada. `useCopilotAction`+`renderAndWaitForResponse` é desenhado para a IA copiloto decidir chamar uma ação — não para uma decisão pendente empurrada pelo servidor. `CartaoDeRecibo.tsx` (T019) reage a `recibo_pendente` diretamente; ver "Known scope cuts" em [protocolo.md](./protocolo.md)
- [ ] T005 [P] **Não feito**: `.env.example` é claim de `cchengy-claude` em `.coord/`, não editado para evitar colisão. Variáveis documentadas em [protocolo.md](./protocolo.md) (`MYSTIQUE_MODO`, `SERVIDOR_PORTA`, `FRONTEND_ORIGIN`, `VITE_API_BASE`) — todas com default funcional, nada bloqueia rodar sem elas

**Checkpoint**: dependências e scaffolding dos dois novos processos prontos; nenhuma delas ainda altera comportamento de `bem`/`mal`/`mystique`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o único ponto de interrupção no motor + o esqueleto do processo `servidor/` + o esqueleto do `frontend/` que consome o stream — nada disso é específico de uma user story, e as três dependem deste alicerce.

**⚠️ CRITICAL**: nenhuma user story começa antes desta fase estar completa.

- [x] T006 Hook `_aguardar_aprovacao` (default `return True`) adicionado em `mystique/mundo.py`, junto aos demais ganchos de versão
- [x] T007 Gate inserido em `good/mundo.py::mapear_habilidade` (o repo renomeou `bem/`→`good/` antes desta implementação — caminho já ajustado), logo após `_identificar`, antes de `_pedir_consentimento`/`_salvar`
- [x] T008 Gate inserido em `evil/mundo.py::roubar_poder` (`mal/`→`evil/`), após o gate de `MUNDO_REAL` já existente (poder que nunca seria roubado de qualquer forma não gera recibo) e antes de `_salvar`
- [ ] T009 [P] **Não feito como pytest em `tests/`**: essa pasta é claim de `cchengy-claude` em `.coord/`. Verificado por script ad-hoc (`MundoBemServidor` com `_chamar` fake): fluxo completo observar→recibo_pendente→aprovar→persistir funciona, `POST /api/recibos/.../decisao` devolve 409 para recibo desconhecido/já resolvido/rejeitado-pelo-juiz, e a suíte `tests/test_offline.py` do time (36 checks) continua 100% verde após os 3 diffs de T006-T008 — sem regressão em `good`/`evil` sem servidor
- [x] T010 [P] `servidor/__init__.py` e `servidor/eventos.py` criados (barramento `asyncio.Queue` por conexão SSE, usando `ag_ui.core.CustomEvent`/`StateSnapshotEvent`)
- [x] T011 `servidor/mundo_servidor.py`: `InterrompivelMixin` + `MundoBemServidor`/`MundoMalServidor`. Também sobrescreve `_salvar` (republica `STATE_SNAPSHOT` a cada persistência — é o único ponto de persistência de todo o motor) e `conversar` (publica `capacidade_observada`), cobrindo T022/T023 no mesmo lugar
- [x] T012 `servidor/app.py`: FastAPI + CORS (`FRONTEND_ORIGIN`), `GET /agui/stream` via `StreamingResponse` + `EventEncoder` do `ag-ui-protocol` (sem `sse-starlette`, ver T001/T002), primeiro evento é sempre `STATE_SNAPSHOT` de `mundo.snapshot()`
- [x] T013 `servidor/__main__.py`: lê `MYSTIQUE_MODO` (aceita `good/evil` e os antigos `bem/mal`), sobe `uvicorn`. Testado ao vivo: `MYSTIQUE_MODO=good python -m servidor` serve `/api/config` e `/agui/stream` de verdade
- [x] T014 [P] `frontend/src/main.tsx`/`App.tsx` criados com a conexão ao stream (`frontend/src/lib/aguiClient.ts`, `EventSource` puro — ver T004) e estado de "Connecting…" até o primeiro `STATE_SNAPSHOT`

**Checkpoint**: verificado ao vivo — `python -m servidor` sobe, `/agui/stream` emite `STATE_SNAPSHOT` real (8 agentes), `/api/config` responde; `tests/test_offline.py` (que exercita `good`/`evil` sem servidor) permanece 100% verde.

---

## Phase 3: User Story 1 - Recibo de confiança (Priority: P1) 🎯 MVP

**Goal**: o humano vê o cartão de recibo (descrição alegada / evidência / veredito) assim que a Mystique tenta reconhecer uma habilidade, e só a decisão dele (aprovar/rejeitar) persiste ou não a conquista.

**Independent Test**: rodar uma conversa até a Mystique tentar reconhecer uma habilidade; confirmar que a UI pausa, renderiza o cartão, e que `workspace/adapters|absorcoes/*.json` só muda depois do clique humano.

### Implementation for User Story 1

- [x] T015 `POST /api/recibos/{recibo_id}/decisao` em `servidor/app.py`, resolve o `asyncio.Future` de `InterrompivelMixin._pendentes`; 409 testado ao vivo (id desconhecido) — como o hook só registra um `Future` quando o juiz aprovou, "veredito aprovado=false" e "já resolvido" caem no mesmo guard (recibo nunca esteve pendente)
- [x] T016 `recibo_pendente` publicado em `_aguardar_aprovacao` (`servidor/mundo_servidor.py`) com o payload exato da tabela; publicado inclusive quando o juiz rejeitou (`veredito.aprovado=false`, sem bloquear a Mystique — ver Acceptance Scenario 4 da US1). Confirmado: nenhum `agente.segredo`/descrição pré-conquista no payload
- [x] T017 `recibo_resolvido` publicado em `_aguardar_aprovacao` ao decidir (`aprovar`/`rejeitar`/`rejeitado_pelo_juiz`); o campo `absorcao_atualizada` do plan.md foi substituído por um `STATE_SNAPSHOT` completo republicado a cada `_salvar` (T011) — mais simples e sempre consistente, o frontend não precisa correlacionar por `recibo_id`
- [x] T018 `POST /api/missoes` (`{mensagem, orcamento?}`) inicia `mystique.agente.executar(...)` em `asyncio.create_task`, com referência guardada num `set` (evita coleta prematura da task). **Simplificado**: sem `Narrador` alternativo — a narração de texto da Mystique continua indo para o console do processo `servidor/` (`avisar(...)`), como já era; nenhum requisito de US1/US2 depende dela (o recibo/passaporte não precisam do texto da conversa)
- [x] T019 [P] [US1] `frontend/src/components/CartaoDeRecibo.tsx`: componente React reagindo a `recibo_pendente`, chamando `POST /api/recibos/{id}/decisao` — **não** via `useCopilotAction`/CopilotKit (ver T004: esse hook é para ação chamada pelo copiloto, não decisão empurrada pelo servidor)
- [x] T020 [US1] Botão "Approve" desabilitado quando `!veredito.aprovado`; cartão some da pilha ao receber `recibo_resolvido` com o mesmo `recibo_id` (filtro no `App.tsx`)

**Checkpoint**: US1 verificada ponta a ponta com um script que simula observar→recibo_pendente→`m.decidir(...)`→persistência→`STATE_SNAPSHOT` com `confirmada`. Falta apenas o teste manual no navegador com `ANTHROPIC_API_KEY` real (não disponível nesta sessão).

---

## Phase 4: User Story 2 - Passaporte de capacidade (Priority: P2)

**Goal**: grid com um cartão por agente, chips de capacidade nos 4 estados, atualizado ao vivo pelos mesmos eventos que já existem no motor.

**Independent Test**: com um workspace já populado (sem nenhuma conversa nova), abrir a UI e conferir que os cartões refletem o estado persistido, incluindo capacidades observadas-mas-não-confirmadas.

### Implementation for User Story 2

- [x] T021 Payload completo de `STATE_SNAPSHOT` em `servidor/mundo_servidor.py::_construir_snapshot`: `{modo, agentes: [{id, nome, apresentacao, externo, capacidades: [{id, estado, motivo}], descartado, essencia_absorvida, progresso}], absorcoes}`. `estado` "rejeitada" só se aplica quando um humano rejeita um recibo já aprovado pelo juiz (rejeição do juiz em si não aponta uma capacidade específica — ver protocolo.md)
- [x] T022 `capacidade_observada` publicado do override de `conversar` em `InterrompivelMixin` (diff de `agente.observados` antes/depois de `super().conversar(...)`) — `mystique/mundo.py` não foi tocado além do hook de T006
- [x] T023 `agente_descartado` publicado do override de `_salvar`, detectando a transição `absorcao.descartado: False→True` — cobre tanto `descartar_agente` explícito quanto o auto-descarte no 100% (`evil/mundo.py:59`/`:94`), sem precisar sobrescrever esses dois métodos separadamente
- [x] T024 [P] [US2] `frontend/src/components/CapacidadeChip.tsx`: 4 estados visuais + `title` (tooltip) com o motivo quando "rejeitada"
- [x] T025 [P] [US2] `frontend/src/components/AgenteCard.tsx`: nome, apresentação, badge "external" quando `agente.externo`, barra de progresso, chips
- [x] T026 [US2] `frontend/src/components/PassaporteGrid.tsx`: renderiza a lista de `AgenteCard` a partir do `Passaporte` mantido em `App.tsx` (substituído inteiro a cada `STATE_SNAPSHOT`, sem merge manual de deltas — mais simples e sempre consistente já que o backend sempre reenvia o snapshot completo, ver T017)

**Checkpoint**: verificado por script — após aprovar um recibo, o `STATE_SNAPSHOT` seguinte já mostra a capacidade como `confirmada` e o progresso atualizado.

---

## Phase 5: User Story 3 - Contraste bem × mal na mesma tela (Priority: P3)

**Goal**: reforço visual da diferença entre custódia revogável (`bem`) e extração permanente (`mal`) no mesmo passaporte.

**Independent Test**: rodar o mesmo cenário de observação/aprovação nos dois modos (dois processos `servidor/` distintos, cada um com seu `MYSTIQUE_MODO`) e comparar os dois passaportes.

### Implementation for User Story 3

- [x] T027 [US3] `GET /api/config` em `servidor/app.py` → `{"modo": "good" | "evil"}`, testado ao vivo
- [x] T028 [US3] `AgenteCard.tsx` exibe "ADAPTER COMPLETE" (modo `good`, 100%, sem descarte) e "DISCARDED" (modo `evil`, `agente.descartado`)
- [x] T029 [US3] `App.tsx` busca `/api/config` no boot, mostra o modo como badge no cabeçalho; sem troca de modo em runtime (cada processo `servidor/` é um modo, igual ao plan.md)

**Checkpoint**: as três user stories implementadas; teste manual completo no navegador com API key real fica para quando houver uma disponível na sessão.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T030 Protocolo documentado em [protocolo.md](./protocolo.md) (não em `README.md` — claim de `cchengy-claude`): tabela de eventos, laço de estado, decisões tomadas — cumpre FR-011/SC-005
- [x] T031 Instruções de execução em [protocolo.md](./protocolo.md) (mesmo motivo: `README.md`/`CLAUDE.md` não editados). Contrato também publicado em `.coord/agents/ednan-claude.md` para o time achar

---

## Estado real ao final desta sessão (build sob feature-freeze de 14:00)

**Feito e verificado**: motor (T006-T008) sem regressão — `tests/test_offline.py` (36 checks) 100%
verde; backend (`servidor/`) rodando de verdade (`python -m servidor`), fluxo completo
observar→recibo→aprovar→persistir→snapshot testado por script; frontend (`frontend/`) compila
limpo (`npm run build`) e implementa CartaoDeRecibo + PassaporteGrid reais sobre o stream.

**Não verificado nesta sessão**: o par backend+frontend rodando junto num navegador de verdade,
com uma missão real da Mystique (precisa de `ANTHROPIC_API_KEY`, não configurada aqui) — próximo
passo antes de gravar qualquer demo com isso.

**Cortes de escopo deliberados** (detalhados em protocolo.md): sem wiring de `@copilotkit/*`
(arquitetura não pedia, ver T004); sem bridge de narração de texto da Mystique para AG-UI (T018);
sem pytest formal em `tests/` (claim de outro agente, T009) — verificação equivalente feita por
script ad-hoc + a suíte existente do time.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sem dependências — pode começar imediatamente
- **Foundational (Fase 2)**: depende da Fase 1 — bloqueia todas as user stories
- **User Stories (Fase 3+)**: todas dependem da Fase 2 completa
  - US1 (P1) não depende de US2/US3
  - US2 (P2) não depende de US1 para funcionar (independent test usa workspace pré-populado), mas reaproveita o `STATE_SNAPSHOT` completado em T021
  - US3 (P3) depende de `AgenteCard.tsx` (T025, de US2)
- **Polish (Fase 6)**: depende das user stories que forem entregues

### Parallel Opportunities

- T002-T005 (Fase 1) em paralelo
- T009, T010 (Fase 2) em paralelo entre si e com T014 depois que T003/T004 terminarem
- T019 (US1) em paralelo com o trabalho de backend de US1 uma vez que o contrato de evento (T016) esteja definido
- T024, T025 (US2) em paralelo entre si

### Dentro de cada user story

- Backend antes do componente de frontend que o consome (o payload/evento precisa existir antes da UI reagir a ele)
- Story completa e testável antes de avançar para a próxima prioridade

---

## Implementation Strategy

### MVP First (User Story 1 apenas)

1. Fase 1: Setup
2. Fase 2: Foundational (bloqueia tudo)
3. Fase 3: User Story 1
4. **Parar e validar**: rodar o Independent Test de US1 (SC-001, SC-003)
5. Demonstrável nesse ponto

### Entrega incremental

1. Setup + Foundational → alicerce pronto
2. + US1 → validar independentemente → demo (MVP)
3. + US2 → validar independentemente → demo
4. + US3 → validar independentemente → demo
