# inferencia-multivac — servir o mundo com Qwen local, sem tocar na Mystique

**Owner:** vago — quem pegar, reivindique no seu `.coord/agents/<handle>.md`
**Status:** draft · **Publicado:** 12:15 por henrique-claude
**Por quê agora:** contrato publicado antes da implementação para que quem for fazer não
precise combinar nada com quem está no motor.

## O que já é verdade no código (verificado, não suposto)

Existem **dois caminhos de modelo independentes**, e só um deles é candidato:

| Caminho | Onde | Quem usa | Trocável? |
|---|---|---|---|
| **Mundo** | `mystique/mundo.py:170` — `anthropic.AsyncAnthropic` | agentes do mundo, **juiz**, consentimento | **sim** |
| **Mystique** | `mystique/agente.py:77` — `ClaudeSDKClient` | a própria Mystique | **não hoje** — ela depende do loop MCP do Agent SDK |

**`Mundo._chamar` é ponto único.** Toda inferência do lado do mundo passa por ali. É a única
função que precisa mudar — e é isso que torna esta troca viável.

## A proposta

Servir os **agentes do mundo** com Qwen no multivac, via endpoint compatível com OpenAI
(`llama-server` do llama.cpp expõe `/v1/chat/completions`). A Mystique continua no Claude.

Isso é a ideia [09-roteamento](../../docs/ideias/09-roteamento.md) levada ao limite: conversa de
personagem é volume e é barata; julgamento é raro e é onde o projeto se apoia.

**O ganho que importa hoje:** o lado do mundo deixa de depender de wifi de evento e de cota de
API. A demo passa a rodar contra hardware que vocês controlam. Isso é robustez real, não enfeite.

## O que o adapter precisa traduzir

Não é drop-in. `_chamar` usa coisas específicas da API da Anthropic, e o loop de ferramentas em
`conversar` lê a resposta no formato Anthropic:

| Depende de | Onde | O adapter precisa |
|---|---|---|
| `beta.messages.create` + `betas` + `fallbacks` | `:171-176` | ignorar; não existe do outro lado |
| `output_config.format.json_schema` | `_json:184` | virar `response_format` json_schema (llama.cpp faz por grammar) |
| `stop_reason == "refusal"` | `_json:185`, `conversar:281` | não existe no OpenAI-compat; mapear para `None` / texto |
| `stop_reason == "tool_use"` | `conversar:283` | virar `finish_reason == "tool_calls"` |
| blocos `content` com `type=="tool_use"`, `.name`, `.input`, `.id` | `conversar:287-292` | virar `message.tool_calls[].function.{name,arguments}` + `.id` |
| `{"type":"tool_result","tool_use_id":...}` | `conversar:293` | virar `{"role":"tool","tool_call_id":...}` |
| `tools[].input_schema` | `conversar:263` | virar `tools[].function.parameters` |
| `tool_choice: {"type":"none"}` | `conversar:274` | virar `tool_choice: "none"` |

**Forma sugerida:** um objeto com o mesmo método `_chamar` que devolve um **objeto no formato
Anthropic** (`SimpleNamespace` com `.content`, `.stop_reason`), para que `conversar` e `_json`
não mudem **nenhuma linha**. Traduz na entrada e na saída, e o resto do motor nem sabe.

Isso também mantém `tests/test_offline.py` válido — ele já simula a API devolvendo
`SimpleNamespace` com `stop_reason` e `content`, ou seja, **o formato-alvo do adapter já está
testado**.

## Contrato de configuração

```bash
MYSTIQUE_WORLD_PROVIDER=anthropic|openai   # default: anthropic
MYSTIQUE_WORLD_BASE_URL=http://<multivac>:<porta>/v1
MYSTIQUE_WORLD_MODEL=<nome do modelo servido>
MYSTIQUE_WORLD_API_KEY=                    # llama-server aceita qualquer valor
```

**Default continua `anthropic`.** Trocar o backend é opt-in por env. Se o multivac cair no meio
da demo, `unset` e a demo volta a rodar. **Isto não é opcional:** nenhuma mudança no caminho
crítico entra hoje sem caminho de volta.

## Riscos, honestamente

1. **Tool calling é o ponto frágil.** O mundo inteiro depende do agente chamar ferramentas —
   é assim que a Mystique **observa** uma habilidade (`agente.observados`). Se o Qwen servido
   não fizer tool calls de forma confiável com o template em uso, **o jogo inteiro para**: sem
   observação, não há conquista. Teste isso primeiro, antes de qualquer outra coisa.
2. **Saída estruturada do juiz.** `_json` precisa de JSON válido contra schema. llama.cpp faz
   via grammar, mas confirme com o schema real do juiz (`poder` enum + `reason`), não com um
   exemplo de brinquedo.
3. **Latência.** São até 6 passos de ferramenta por conversa. Se cada passo demorar, a demo
   fica lenta em tela — pior que cara.
4. **Rede local.** Se o multivac não for alcançável da máquina que grava o vídeo, isso vira um
   risco no pior momento possível.

## Ordem de teste (30 min, antes de escrever adapter nenhum)

1. `curl` no `/v1/chat/completions` do multivac, resposta simples. Funciona?
2. Mesma chamada **com `tools`** e um schema trivial. Ele devolve `tool_calls`?
3. Mesma chamada com `response_format` json_schema usando **o schema real do juiz**.
4. Só se 1–3 passarem: escrever o adapter.

**Se o passo 2 falhar, o Qwen serve o consentimento e talvez o juiz, mas não os agentes do
mundo** — e aí o valor cai muito. Descubra isso em 10 minutos, não em 60.

## Perguntas em aberto (preciso de resposta para fechar o contrato)

- O que é o multivac — máquina na LAN do evento, VPS, laptop de alguém? URL e porta?
- Alcançável de **todas** as máquinas, inclusive a que vai gravar?
- Qual Qwen exatamente (tamanho, quantização) e servido por `llama-server`?
- Ele já foi testado fazendo **tool calling**, ou é suposição?

## Veredicto de tempo

São 12:15; freeze às 14:00. Isto é **a mudança mais arriscada possível** — está no caminho de
toda conversa do mundo. Faz sentido **se e somente se** os passos 1–3 passarem rápido e o
default `anthropic` continuar intacto como volta.

**Não faça isso antes do vídeo estar gravado.** Grave com o que funciona hoje; troque o backend
depois, com a submissão já garantida.
