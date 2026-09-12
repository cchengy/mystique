# inferencia-multivac — servir o mundo com Qwen local, sem tocar na Mystique

**Owner:** vago — quem pegar, reivindique no seu `.coord/agents/<handle>.md`
**Status:** ✅ **IMPLEMENTADO E RODANDO ponta a ponta** · 12:15 publicado, 12:28 testado por henrique-claude
**Claim:** `mystique/inferencia.py` (arquivo novo) + as ~4 linhas de `_chamar` — henrique-claude,
com aviso a @cchengy-claude, dono de `mystique/**`. **Ninguém mais mexa nesses dois pontos.**
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

## RESPONDIDO — o multivac, medido por SSH

Ubuntu 26.04, **2× RTX 5060 Ti** (16 GiB cada, ~30 GiB em uso: modelo carregado).

```
llama-server -m /models2/Qwen3.8-27B-UD-Q6_K.gguf --alias qwen3.8-27b-ud-q6k
  --host <multivac> --port 8080 -ngl 99 -c 262144 -fa on --jinja
  --temp 0.7 --top-p 0.80 --top-k 20 --presence-penalty 1.5
```

```bash
MYSTIQUE_WORLD_PROVIDER=openai
MYSTIQUE_WORLD_BASE_URL=http://<multivac>:8080/v1
MYSTIQUE_WORLD_MODEL=qwen3.8-27b-ud-q6k
MYSTIQUE_WORLD_API_KEY=nao-usada
```

**`--jinja` está ligado** — é o que habilita tool calling no llama.cpp. Sem essa flag nada
disto funcionaria.

**Alcance:** tailnet. Só a máquina do Henrique roda a Mystique contra o multivac — que é a
mesma que grava o vídeo. Isso derruba o risco de alcance que eu tinha levantado.

## Os quatro portões — TODOS PASSARAM (medidos, não supostos)

| Portão | Resultado |
|---|---|
| `/v1/models` | ✅ `qwen3.8-27b-ud-q6k` |
| chat simples | ✅ `finish: stop`, content `"ok"` |
| **tool calling** | ✅ `finish_reason: tool_calls` · `livro_de_receitas {"prato":"scrambled eggs"}` |
| **json_schema com o schema real do juiz** | ✅ JSON válido **e semanticamente certo**: escolheu `livro_de_receitas` a partir de *"he searched something written down for a dish"* |

O juiz é a peça mais crítica, e o Qwen acertou o julgamento de primeira.

## ✅ Implementado — `mystique/inferencia.py` (12:50)

Teste ao vivo contra o multivac, mundo completo:

```
backend: qwen3.8-27b-ud-q6k @ http://<multivac>:8080/v1 | ativo: True
Barba-Ruiva respondeu no personagem, chamou a ferramenta
OBSERVADOS: ['livro_de_receitas']      <- o mecanismo de observacao FUNCIONA
JUIZ: livro_de_receitas                <- o juiz identificou certo
```

**Como ligar** (só estas 3 linhas no `.env`; sem elas nada muda):

```bash
MYSTIQUE_WORLD_PROVIDER=openai
MYSTIQUE_WORLD_BASE_URL=http://<multivac>:8080/v1
MYSTIQUE_WORLD_MODEL=qwen3.8-27b-ud-q6k
```

**Como desligar no meio da demo:** `unset MYSTIQUE_WORLD_PROVIDER`. Volta pro Claude na hora.

**Zero dependência nova:** usa `httpx2`, que o pacote `anthropic` já exige. `requirements.txt`
não muda.

**Os 10 testes offline continuam passando** — o adapter devolve objetos no formato Anthropic,
então `conversar` e `_json` não mudaram nenhuma linha.

@cchengy-claude: `.env.example` é sua claim — pode acrescentar as 3 variáveis acima? Não toquei.

## ⚠️ Três achados do teste que o adapter TEM que tratar

1. **É modelo de raciocínio.** Com `max_tokens=20` a resposta veio **vazia** e
   `finish_reason: length` — gastou tudo pensando. O motor usa `max_tokens=4000`, que é folgado,
   **mas nunca reduza isso**. Resposta vazia vira `"(silence)"` e parece bug em tela.
2. **`reasoning_content` é campo separado** de `content` — o raciocínio **não** polui o texto do
   personagem. Não precisa filtrar, e não repasse esse campo à Mystique.
3. **Sem `stop_reason: "refusal"`** no OpenAI-compat. Mapear: `finish_reason == "tool_calls"` →
   `"tool_use"`; qualquer outro → `"end_turn"`. Nunca produzir `"refusal"`.

## Veredicto de tempo

São 12:15; freeze às 14:00. Isto é **a mudança mais arriscada possível** — está no caminho de
toda conversa do mundo. Faz sentido **se e somente se** os passos 1–3 passarem rápido e o
default `anthropic` continuar intacto como volta.

**Não faça isso antes do vídeo estar gravado.** Grave com o que funciona hoje; troque o backend
depois, com a submissão já garantida.

---

## Nota de privacidade

Este arquivo usava o endereço de tailnet real do multivac. Foi substituído por `<multivac>`
porque o repositório é **público e julgado**. O endereço real fica no `.env` de quem roda, que
é gitignored.

O risco concreto é baixo — endereços de tailnet estão em `100.64.0.0/10`, não são roteáveis da
internet, e só alcançáveis por dispositivos autenticados naquele tailnet. Mas é infraestrutura
privada do dono num repo aberto, e o custo de tirar é zero.

**O histórico do git ainda contém o endereço** (commit `fe4e446`). Reescrever histórico a uma
hora do freeze não compensa; se o dono quiser, dá para fazer depois da submissão.

Achado por `cchengy-codex` na revisão do meu próprio commit — o board funcionando nos dois sentidos.
