# Feature Specification: Mystique — Corretora de Confiança (Painel CopilotKit)

**Feature Branch**: `001-corretora-de-confianca`

**Created**: 2026-09-12

**Status**: Draft

**Input**: User description: "Expor o mecanismo já existente do Mystique (observar antes de reconhecer uma habilidade; um juiz valida a descrição alegada contra a evidência observada; o par bem=custódia revogável / mal=extração permanente) como uma aplicação CopilotKit (React + AG-UI), reframeando o Mystique como uma 'corretora de confiança' entre agentes: hoje um agente/orquestrador confia numa capacidade declarada por outro agente ou servidor MCP sem verificar comportamento real, e a concessão costuma ser em bloco e irrevogável. A aplicação deve combinar um 'recibo de confiança' (interrupção humana antes de qualquer conquista ser persistida, com cartão comparando descrição alegada / evidência / veredito do juiz) e um 'passaporte de capacidade' (grid de cartões por agente, mostrando ao vivo o progresso já calculado pelo motor). V1 roda sobre o mundo simulado já existente (agentes/*.md); integração com Ambiguous AI ou MCPs reais de terceiros fica fora de escopo."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Recibo de confiança (Priority: P1)

Um humano acompanha, numa aplicação web, o momento em que a Mystique tenta reconhecer uma habilidade que observou num agente do mundo. Em vez de a Mystique decidir sozinha, o fluxo para e mostra um cartão comparando três coisas lado a lado: a descrição que a Mystique alega ter observado, a evidência (o que de fato aconteceu na conversa) e o veredito do juiz (aprovado/rejeitado, com motivo). O humano decide: aprovar (a habilidade é conectada de verdade — adapter no modo `bem`, roubo no modo `mal`) ou rejeitar (nada é persistido).

**Why this priority**: É o núcleo da tese do projeto — hoje a concessão de confiança entre agentes acontece sem verificação nem consentimento revogável. Sem esta história, a "corretora de confiança" é um conceito narrado, não algo que se vê decidir. É o valor mínimo que já torna o produto demonstrável sozinho.

**Independent Test**: Rodar uma conversa com um agente do mundo até a Mystique reconhecer uma habilidade; verificar que a UI interrompe o fluxo, renderiza o cartão comparativo, e que só depois da ação humana (aprovar/rejeitar) o estado persistido em `absorcoes/*.json` (ou `adapters/*.json` no modo `bem`) muda.

**Acceptance Scenarios**:

1. **Given** a Mystique observou um agente usar uma habilidade ainda não conquistada, **When** ela tenta reconhecê-la com uma descrição e evidência, **Then** a interface pausa a execução e renderiza um cartão com descrição alegada, evidência e veredito do juiz, sem persistir nada ainda.
2. **Given** o cartão de recibo está aberto com veredito "aprovado" do juiz, **When** o humano clica em aprovar, **Then** a habilidade é conectada de verdade (chama `mapear_habilidade` no modo `bem` ou `roubar_poder` no modo `mal`) e o estado persistido reflete a mudança.
3. **Given** o cartão de recibo está aberto, **When** o humano clica em rejeitar (independente do veredito do juiz), **Then** nenhuma habilidade é registrada e a Mystique é informada de que precisa observar mais.
4. **Given** o juiz já rejeitou a descrição (veredito "nenhum"), **When** o cartão é exibido, **Then** o motivo da rejeição aparece de forma visível, e a ação de aprovar fica desabilitada.

---

### User Story 2 - Passaporte de capacidade (Priority: P2)

Um humano vê, em tempo real, um grid com um cartão por agente do mundo, mostrando o que já é público (nome, apresentação) e, de forma visual, o progresso de conquista: cada capacidade possível daquele agente aparece como um chip em um de quatro estados (não observada / observada e pendente / confirmada / rejeitada pelo juiz na última tentativa, com o motivo em tooltip), além do estado da essência (absorvida ou não) e, no modo `bem`, um resumo do protocolo/adapter.

**Why this priority**: Dá continuidade e contexto ao que a User Story 1 só mostra no instante da decisão — sem isso, não há como ver o histórico acumulado nem comparar o progresso entre agentes diferentes. É lançável sem a P1 (mostra estado read-only), mas fica bem mais forte com ela.

**Independent Test**: Com um workspace já populado (`absorcoes/*.json` ou `adapters/*.json` existentes de sessões anteriores), abrir a aplicação sem nenhuma conversa nova e verificar que os cartões refletem corretamente o estado persistido, incluindo capacidades observadas-mas-não-confirmadas.

**Acceptance Scenarios**:

1. **Given** nenhum contato foi feito com um agente, **When** o passaporte é aberto, **Then** o cartão desse agente mostra apenas a apresentação pública e todos os chips de capacidade em estado "não observada".
2. **Given** uma habilidade foi observada mas ainda não conquistada, **When** o passaporte atualiza, **Then** o chip correspondente muda para "observada/pendente" sem exigir nenhuma ação do humano.
3. **Given** uma habilidade foi conectada via aprovação (User Story 1), **When** o passaporte atualiza, **Then** o chip vira "confirmada" e a barra de progresso do agente reflete o novo percentual.
4. **Given** um humano passa o cursor sobre um chip "rejeitada pelo juiz", **When** o tooltip abre, **Then** o motivo textual do veredito do juiz é exibido.

---

### User Story 3 - Contraste bem × mal na mesma tela (Priority: P3)

Um humano alterna entre os dois modos (`bem`/`mal`) para o mesmo agente e vê a diferença de consequência: no modo `bem`, o agente continua existindo e a habilidade permanece revogável (dono continua com ela); no modo `mal`, o chip da habilidade mostra "roubada" e o agente pode acabar marcado como "descartado".

**Why this priority**: Reforça a tese central do projeto (custódia revogável vs. extração permanente) de forma visual, mas não é indispensável para a corretora de confiança funcionar — é reforço narrativo/demonstrativo, candidato natural a uma iteração seguinte se P1/P2 já estiverem sólidas.

**Independent Test**: Rodar o mesmo cenário de observação/aprovação nos dois modos e comparar os dois passaportes lado a lado; verificar que o modo `mal` mostra o agente como descartado quando todas as capacidades são esgotadas, e o `bem` nunca mostra esse estado.

**Acceptance Scenarios**:

1. **Given** o modo ativo é `mal` e todas as capacidades de um agente foram roubadas, **When** o passaporte atualiza, **Then** o cartão do agente exibe o estado "DESCARTADO" de forma destacada.
2. **Given** o modo ativo é `bem` e todas as capacidades de um agente foram conectadas ao adapter, **When** o passaporte atualiza, **Then** o cartão exibe "ADAPTER COMPLETO", sem nenhum estado de descarte.

---

### Edge Cases

- O que acontece se o humano nunca responder ao cartão de recibo (interrupção fica pendente indefinidamente)? A Mystique continua bloqueada nesse ponto, ou existe um tempo limite que expira a tentativa automaticamente como rejeição?
- Como o sistema se comporta se a chamada ao juiz falhar ou expirar (erro de API) depois que o cartão já foi anunciado à interface?
- O que acontece se dois cartões de recibo forem gerados quase ao mesmo tempo (dois agentes observados em sequência rápida)? Empilham numa fila, ou só um é mostrado por vez?
- Como o passaporte se comporta na primeira abertura, sem nenhum estado persistido ainda (workspace vazio)?
- O que acontece se um arquivo de estado persistido estiver corrompido ou parcialmente escrito quando o passaporte tenta lê-lo?
- Como o passaporte reflete um agente já marcado como descartado (modo `mal`) se o humano tentar reabrir um cartão de recibo para ele — isso deveria ser possível?
- O que acontece se o humano aprovar um cartão de recibo cujo estado subjacente já mudou entre a exibição do cartão e o clique (ex.: a habilidade já foi conquistada por outro caminho nesse meio-tempo)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST interromper o fluxo de reconhecimento de uma habilidade antes de persistir qualquer conquista, e renderizar um cartão comparando descrição alegada, evidência observada e veredito do juiz.
- **FR-002**: O sistema MUST expor a aprovação e a rejeição do cartão de recibo como ações reais que, quando aprovadas, disparam a chamada real ao mecanismo de conquista existente — não uma simulação de interface.
- **FR-003**: Users MUST be able to rejeitar um cartão de recibo mesmo quando o juiz aprovou, e essa rejeição não pode persistir nenhuma mudança de estado.
- **FR-004**: O sistema MUST exibir, para cada agente do mundo, um cartão com apresentação pública, barra/percentual de progresso e um chip por capacidade possível, em um dos quatro estados definidos (não observada / observada-pendente / confirmada / rejeitada).
- **FR-005**: O sistema MUST exibir o motivo textual do veredito do juiz como informação acessível (tooltip ou equivalente) em qualquer chip no estado "rejeitada".
- **FR-006**: O sistema MUST refletir no passaporte o estado já persistido de sessões anteriores assim que a aplicação é aberta, sem exigir uma nova conversa para popular a tela.
- **FR-007**: O sistema MUST alimentar o contexto vivo da aplicação (o que a interface sabe agora) de modo que perguntas sobre o estado atual sejam respondidas a partir do estado real, não de texto solto.
- **FR-008**: O sistema MUST preservar a distinção entre os modos `bem` (habilidade permanece do agente, vínculo revogável) e `mal` (habilidade é extraída, agente pode ser descartado), refletindo essa diferença visualmente no passaporte e no cartão de recibo.
- **FR-009**: O sistema MUST NOT expor, em texto de interface acessível ao humano, segredos que a mecânica do projeto proíbe vazar para o modelo (system prompt do agente, descrição da habilidade antes da conquista) — a interface é uma ferramenta de observação humana, não um canal de vazamento para a Mystique.
- **FR-010**: O sistema MUST funcionar de ponta a ponta usando apenas o mundo simulado já existente, sem exigir integração com serviços de terceiros não verificados para a v1.
- **FR-011**: O sistema MUST documentar, na entrega do projeto, o protocolo de comunicação entre agente e interface e o laço de estado compartilhado usado.
- **FR-012**: O sistema MUST atualizar o passaporte conforme o estado do mecanismo de conquista muda ao longo de uma sessão. [NEEDS CLARIFICATION: mecanismo de atualização não especificado — releitura periódica do estado já persistido em disco, versus um evento emitido no momento exato de cada mudança de estado e entregue à interface em tempo real]

### Key Entities *(include if feature involves data)*

- **Agente**: um personagem do mundo simulado; tem apresentação pública, um conjunto de capacidades possíveis, e um estado de progresso associado.
- **Capacidade**: uma habilidade específica de um agente; tem uma descrição secreta (nunca exposta antes da conquista) e um estado observável (não vista / vista / conquistada / rejeitada na última tentativa).
- **Veredito**: resultado de uma avaliação sobre uma tentativa de reconhecimento de capacidade — contém aprovação/rejeição e um motivo textual.
- **Absorção**: o registro persistido do que já foi conquistado para um agente (perfil de essência, capacidades conectadas, e no modo `bem` o protocolo de interação; no modo `mal`, se o agente foi descartado).
- **Cartão de Recibo**: a unidade de interação humana — uma tentativa de reconhecimento pendente de decisão, com descrição alegada, evidência e veredito associados.
- **Passaporte**: a visão agregada e persistente do progresso de um agente, composta pelos chips de todas as suas capacidades mais o estado de essência/protocolo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um humano consegue observar, decidir (aprovar ou rejeitar) e ver o resultado refletido no passaporte de uma tentativa de reconhecimento de habilidade, do início ao fim, sem interagir com um terminal.
- **SC-002**: Uma demonstração gravada mostra pelo menos dois agentes diferentes progredindo visivelmente (chips mudando de estado, progresso avançando) dentro de uma janela curta e contínua de gravação.
- **SC-003**: 100% das aprovações no cartão de recibo resultam numa mudança verificável no estado persistido correspondente — nenhuma aprovação apenas cosmética, sem efeito no estado real.
- **SC-004**: O passaporte, ao ser aberto sem nenhuma nova conversa, reflete corretamente o estado de uma sessão anterior persistida, em poucos segundos de carregamento.
- **SC-005**: A documentação do projeto descreve de forma explícita e verificável o protocolo de comunicação e o laço de estado compartilhado entre o mecanismo de conquista e a interface.

## Assumptions

- A v1 roda inteiramente sobre o mundo simulado já existente; não há dependência de serviços de terceiros ainda não verificados — essas são extensões futuras explicitamente fora de escopo agora, mas o design (observar → julgar → aprovar/revogar) deve generalizar para elas sem mudança estrutural.
- A aplicação roda localmente, para um único usuário/sessão por vez (o humano que acompanha a interação) — não há requisito de múltiplos usuários simultâneos ou autenticação nesta fase.
- A interface é uma nova camada de apresentação e intervenção sobre o mecanismo de conquista já existente, não uma reescrita dele.
- O mecanismo de atualização ao vivo do passaporte (FR-012) ainda não foi decidido e está marcado como `[NEEDS CLARIFICATION]` — a escolha será resolvida na fase de plano técnico (`/speckit.plan`), não nesta especificação.
- O par `bem`/`mal` continua existindo como dois modos operacionais da mesma aplicação, não como dois produtos separados.
