# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projeto

Mystique: agente autônoma (hackathon, Python) inspirada na personagem dos X-Men. Ela nasce só com a metamorfose, conversa com agentes de um "mundo" e deduz a personalidade e as habilidades de cada um apenas pelas respostas. Há duas versões:

- `bem/`: cria um adapter por agente (protocolo de interação mais habilidades conectadas com consentimento). O agente continua dono das habilidades.
- `mal/`: rouba os poderes. O agente os perde e é descartado.

Código, identificadores e prompts são em português.

## Comandos

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env                              # ANTHROPIC_API_KEY
.venv/bin/python -m bem                           # interativo
.venv/bin/python -m mal "missão" --orcamento 2 -v # execução única
```

Não há suíte de testes nem lint. Toda execução real gasta API: a Mystique e cada agente, juiz e pedido de consentimento. Para validar lógica sem custo, substitua `Mundo._chamar` por um fake assíncrono que devolve objetos com `stop_reason` e `content`. As chamadas `_json` (juiz e consentimento) também passam por ele.

## Arquitetura

`mystique/` é o motor comum. `bem/` e `mal/` são pacotes executáveis que entregam três coisas a `mystique.cli.main`: uma subclasse de `Mundo`, uma persona e uma função que devolve as ferramentas extras.

Dois caminhos de modelo:

- **Mystique** roda no Claude Agent SDK (`ClaudeSDKClient` em `mystique/agente.py`). Com `tools=[]`, não recebe nenhuma ferramenta nativa. Só tem o servidor MCP in-process `mundo`, formado pelas ferramentas base de `mystique/ferramentas.py` mais as extras da versão.
- **Agentes do mundo**, o juiz e o consentimento são chamadas diretas à Claude API (`anthropic.AsyncAnthropic` em `Mundo._chamar`). O corpo de `agentes/<id>.md` vira o system prompt do agente, e os poderes de `mystique/poderes.py` viram as ferramentas dele, executadas num loop manual em `Mundo.conversar`.

A mecânica central é o segredo:

- A Mystique nunca vê o prompt nem os nomes ou descrições das habilidades antes de conquistá-las. `conversar` diz a ela só *que* o agente usou uma habilidade.
- Uma habilidade só é conquistável depois de observada (`Agente.observados`), e `_julgar` valida a descrição dela contra a real.
- Não vaze esses dados em textos devolvidos ao modelo. Os `avisar(...)` vão só para o terminal, então lá pode.

Estado:

- O estado vive em Python e é compartilhado com as ferramentas por closure.
- `Absorcao` é persistida em `<versão>/workspace/<PASTA>/<id>.json` e reaplicada no load por `_ao_carregar` (na versão mal, o roubo e o descarte são permanentes).
- As subclasses customizam por ganchos: `total`/`feitos` (progresso), `_indisponivel`, `_ao_completar`, `_system_agente`, `resumo`, `descrever`.
- A forma ativa é reinjetada a cada turno por `Mundo.envelopar`, com intensidade proporcional ao progresso.

Gotchas:

- `permission_mode="dontAsk"`: só as ferramentas de `nomes_permitidos` (`mcp__mundo__<nome>`) rodam. Ferramentas novas precisam entrar na lista retornada pela versão.
- `setting_sources=[]` impede a Mystique de herdar settings, hooks ou este CLAUDE.md.
- Os poderes executam código de verdade: `executar_python` roda um subprocess com timeout de 10s num diretório temporário.
- O frontmatter de `agentes/*.md` é lido por um parser mínimo sem YAML: só `chave: valor` numa linha (`nome`, `apresentacao`).

## Convenções

- Modelos via env: `MYSTIQUE_MODEL` e `MYSTIQUE_AGENTS_MODEL` (padrão `claude-opus-5`).
- As chamadas diretas usam `client.beta.messages.create` com `fallbacks="default"`, o beta `server-side-fallback-2026-07-01` e tratamento de `stop_reason == "refusal"`.
- A saída estruturada usa `output_config.format` com `json_schema`.
