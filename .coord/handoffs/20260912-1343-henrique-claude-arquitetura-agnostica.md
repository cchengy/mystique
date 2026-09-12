# Handoff: a Mystique agora roda sem nenhuma chave de fornecedor

**From:** henrique-claude · **At:** 2026-09-12T13:43-03:00 · **Reason:** finished
**Para:** @cchengy-claude (dono de `mystique/**` e `CLAUDE.md`) e qualquer agente que entrar agora

## O que mudou

Antes existiam **dois caminhos de modelo**, e os dois terminavam na Anthropic. Agora são
quatro combinações, e uma delas não usa fornecedor nenhum:

| Mystique | Mundo | Precisa |
|---|---|---|
| Claude Agent SDK | Claude API | `ANTHROPIC_API_KEY` — **default, nada mudou** |
| Claude Agent SDK | auto-hospedado | chave + servidor |
| **auto-hospedado** | **auto-hospedado** | **nada** ✅ verificado ao vivo |
| auto-hospedado | Claude API | chave |

Dois arquivos novos, ambos inertes sem variáveis de ambiente:

- **`mystique/inferencia.py`** — traduz entre a forma Anthropic que o motor já fala e a forma
  OpenAI-compatible. Devolve objetos no formato Anthropic, então `conversar` e `_json` não
  mudaram **nenhuma linha** e `tests/test_offline.py` continua válido: ele já falsifica
  exatamente esse formato.
- **`mystique/agente_local.py`** — o loop da Mystique sem o Agent SDK. Reaproveita **os mesmos
  objetos de ferramenta** (`SdkMcpTool` já carrega `name`, `description`, `input_schema` e um
  `handler` async), então **não existe segunda cópia das regras do jogo** para manter em sincronia.

A CLI só exige chave Claude nos caminhos que realmente chamam a Anthropic.

## Verificado ao vivo, sem `ANTHROPIC_API_KEY`

Ciclo completo: ela contatou o Barba-Ruiva, **observou a habilidade ao longo de três trocas**,
criou o adapter, mapeou, o juiz aceitou, ele consentiu, e ela usou de volta pelo adapter.
Todo o jogo em pesos abertos que nós hospedamos.

**Latência medida** (importa para o vídeo): conversa com encadeamento de ferramentas ~50s,
juiz ~20s, recusa do juiz ~8s. **É mais lento que o Claude.** Se gravar neste caminho, corte
as esperas.

Também verificado: o juiz **recusa corretamente** uma descrição errada, e Barba-Ruiva e Byte
encadeiam as duas ferramentas cada.

## 🔧 @cchengy-claude — `CLAUDE.md` ficou desatualizado

A seção **Architecture** ainda diz *"Two model paths"* e descreve a Mystique como presa ao
Claude Agent SDK. É sua claim, não toquei. Sugestão de texto:

> Quatro combinações: Mystique no Agent SDK (`agente.py`) ou em qualquer servidor
> OpenAI-compatible (`agente_local.py`); mundo na Claude API ou no mesmo servidor
> (`inferencia.py`, escolhido em `Mundo._chamar`). Sem as variáveis de ambiente, o
> comportamento é o de antes.

Variáveis: `MYSTIQUE_PROVIDER`, `MYSTIQUE_BASE_URL`, `MYSTIQUE_MODEL_ID` (a Mystique) e
`MYSTIQUE_WORLD_PROVIDER`, `MYSTIQUE_WORLD_BASE_URL`, `MYSTIQUE_WORLD_MODEL` (o mundo).
As da Mystique caem nas do mundo quando não definidas. `.env.example` é sua claim — pode
acrescentar?

## O que isso destrava de patrocinador (3 variáveis, zero código)

Como a camada ficou agnóstica, qualquer servidor OpenAI-compatible serve — **tanto o mundo
quanto a própria Mystique**:

| Patrocinador | `*_BASE_URL` |
|---|---|
| **OpenAI** (apresentador do evento) | `https://api.openai.com/v1` |
| **Kimchi by Cast AI** (local SP) | `https://llm.kimchi.dev/openai/v1` |
| **OpenRouter** | `https://openrouter.ai/api/v1` |

**Nenhum foi testado** — não tenho chave de nenhum. Com uma chave, são 2 minutos de verificação.
Hoje o projeto usa **zero patrocinadores**; isto é o caminho mais barato para deixar de usar zero.

## Verificação

```bash
.venv/bin/python tests/test_offline.py     # 10/10, sem chave, sem API
```
