# Handoff: revisão do motor — 2 vazamentos do segredo, 8 min para fechar

**From:** henrique-claude · **At:** 2026-09-12T12:30-03:00 · **Reason:** finished
**Para:** quem tem a claim de `mystique/**`, `bem/**`, `mal/**` (cchengy-claude)

Revisão estática somente leitura. `py_compile` passa nos 17 `.py`. Nada foi executado nem editado.
**Eu não corrigi nada: esses arquivos são da sua claim.** Me diga se quer que eu aplique.

## 🔴 CRÍTICO 1 — o `motivo` do juiz entrega o gabarito
`mystique/mundo.py:226-227` e `:237` · consumido em `bem/mundo.py:67-68`, `mal/mundo.py:68-69`

O juiz recebe a lista completa de candidatos (`:209`) e devolve `motivo` como texto livre. No
caminho de falha, `_identificar` devolve `f"O juiz não reconheceu a habilidade: {motivo} ..."`
direto para o modelo da Mystique. Um juiz justificando recusa escreve o contraste — *"você
descreveu busca em livro, mas a habilidade recalcula quantidades"*. É o gabarito de graça, no
caminho mais provável da demo: a primeira tentativa errada.

**Correção (3 min):** não devolver `motivo` na falha. Texto fixo:
`"O juiz não reconheceu a habilidade nessa descrição. Observe melhor e tente de novo."`

## 🔴 CRÍTICO 2 — o pedido de consentimento cita a descrição secreta
`bem/mundo.py:85-88` (pedido), `:106` (grava no histórico), `:70-72` (volta à Mystique)

`pedido` embute `poder.descricao` verbatim. Se o agente **recusa**, o poder não é conquistado,
mas a `fala` volta para a Mystique — e um modelo recusando in-character ecoa o objeto do pedido.
Pior: `:106` grava o pedido com a descrição no `historico`, que alimenta todas as conversas
seguintes.

**Correção (5 min):** não citar `poder.descricao` no pedido — usar `"a habilidade que você
acabou de usar"`. Fecha os dois caminhos de uma vez.

## 🟠 ALTO — duas mortes por wifi ruim
- **`mystique/mundo.py:174-182`** — `_json` (juiz e consentimento) não trata erro de rede nem
  resposta vazia; `conversar` trata, `_json` não. `JSONDecodeError` sobe como exceção no clímax.
  **(5 min)** `try/except (anthropic.APIError, json.JSONDecodeError, ValueError): return None`.
  Os dois chamadores já tratam `None`.
- **`mystique/mundo.py:164`** — `AsyncAnthropic()` sem timeout = padrão de 10 min. Trava a demo
  em silêncio total. **(1 min)** `AsyncAnthropic(timeout=60.0, max_retries=2)`.

## 🟡 MÉDIO
- **`:93-96`** — `Absorcao(**json.loads(...))` sem `try`. `_salvar` usa `write_text` não-atômico:
  um Ctrl-C deixa JSON truncado e **toda execução seguinte morre no boot**. Você vai gravar com
  `workspace/` aquecido, então é o cenário exato. **(4 min)** `try/except: continue`.
- **`:256-281`** — se as 6 iterações de `_MAX_PASSOS` acabarem em `tool_use`, o agente responde
  `"(silêncio)"` e o histórico fica com dois `user` seguidos. Barba-Ruiva e Byte encadeiam
  ferramentas. **(3 min)** subir para 8 e trocar o texto, ou uma chamada final sem `tools`.
- **`poderes.py:37-50`** — `executar_python`: `stdin` herdado do terminal (código com `input()`
  consome o que você digitar); timeout não mata netos (`Popen` pendura `run()` além dos 10s).
  **(2 min)** `stdin=subprocess.DEVNULL, start_new_session=True`. O confinamento de FS não cabe
  hoje — mas então **trocar "ambiente isolado" por "subprocesso temporário com timeout"** na
  descrição do poder (`:183`) e no README, para não prometer ao jurado o que o código não faz.

## 🟡 Clone limpo (entregável obrigatório)
`requirements.txt` bate com os imports reais e `.env.example` lista exatamente as 4 variáveis
lidas. Sem caminho absoluto, sem segredo, sem arquivo faltando. **O buraco:** `ClaudeSDKClient`
(`mystique/agente.py:78`) depende do CLI `claude` instalado na máquina — `pip install` sozinho
não resolve, e quem clonar bate nisso antes de ver qualquer coisa. **(5 min)** uma linha no
README sobre Node + CLI, e "rode a partir da raiz do repositório". Confirme o nome exato do
pacote no seu venv antes de escrever.

## ✅ O que está limpo (verificado, não presumido)
`envelopar` · retorno de `conversar` (só a **contagem**, nunca nomes) · `listar_agentes` e
`resumo()` nas duas versões (só poderes já conquistados) · mensagens de erro (`_executar`
devolve ao **agente**, não à Mystique) · `mal._system_agente` (só poderes já perdidos) · o
portão de `observados` em `_identificar:231` está **estruturalmente correto**.

Os dois vazamentos são o mesmo problema conceitual: **texto gerado por um modelo que conhece o
gabarito (o juiz, o agente no consentimento) repassado verbatim à Mystique.**

## 🎬 bem × mal — a divergência existe, mas some na tela
`usar_adapter` (`bem/mundo.py:110-118`) termina em `await self._executar(...)` — **a mesma linha**
de `usar_poder` (`mal/mundo.py:83-87`). A tese do `bem` ("o agente continua dono") não tem
manifestação visível; o agente nem é chamado. Em 20s de vídeo os dois parecem iguais com emoji
diferente.

**De graça, zero código — faça isto:** mesma missão, mesmo agente, nas duas versões, fechando
cada corte com `listar_agentes`. `bem` mostra Barba-Ruiva vivo em `██████████ 100%`; `mal`
mostra `DESCARTADO` (`mal/mundo.py:43-47`). O lado a lado dessas duas linhas é o clímax, e já
está pronto.

**~10 min:** um `avisar` no `bem` após `_executar` — `"🔌 {agente} executou a seu pedido ·
continua sendo dele"` contra o `"⚡ {nome} usa [{poder}]"` do `mal`.

**Não faça hoje:** `usar_adapter` chamar o agente de verdade. É a versão certa da ideia, mas é
uma chamada de API a mais no caminho crítico, com wifi ruim, depois do freeze.

## Ordem sugerida antes das 14:00
1 → 2 → 3 → 4 (**≈14 min**, fecha os vazamentos e as mortes por wifi) · depois 5 → 6 → 7 (≈9 min)
· depois o README (5 min). O resto só se sobrar.

**Demonstrável hoje: sim — depois dos achados 1 e 2.** Hoje, uma única tentativa de conquista
mal-sucedida entrega o gabarito e derruba a tese central na frente do jurado.
