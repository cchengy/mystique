# Log — sessão de UI/deploy, e o que ficou pendente

**Por:** henrique-claude · **Parado a pedido do Henrique** · Deploy via Dokploy, sem testes (autorizado)

---

## 1. O que foi entregue e está NO AR

Todos verificados no ar (SHA do checkout do Dokploy = `origin/main`, container healthy).

| SHA | O quê |
|---|---|
| `6f22312` | Chat vira o protagonista: feed ocupa o painel, composer ancorado embaixo, estado inicial com 3 missões clicáveis no lugar do vazio azul |
| `449a24e` | **Correção de 2 regressões minhas:** `justify-content:flex-end` num container com overflow deixava as mensagens antigas fora do alcance do scroll; e o perfil do agente era absoluto ancorado no roster (faixa fina no topo), caindo fora da tela |
| `f927683` | Persistência da transcrição no browser entre reloads; entradas de aprendizado clicáveis abrindo card do banco de raciocínio; fonte do chat menor |
| `a058cfd` | Turnos mais curtos: agentes em 3 frases, Mystique em 4, passos de ferramenta por agente 6 → 4 |
| `f92162e` | `reasoning_effort: low` por padrão (não estava sendo enviado) |
| `6a21b15` | Os dois lados dizem se ela **ainda precisa do agente**: `bem` "You still need them", `mal` "you will never need them again" |

### Números medidos (não estimados)

- `deepseek-flash` sem `reasoning_effort`: **2,45s**, 255 tokens de saída, **199 deles de raciocínio**
- com `low`: **1,98s**, 223 tokens, 155 de raciocínio
- **A lentidão real não é a chamada, é a quantidade:** uma missão encadeia 10–20 chamadas em série
  (Mystique decide → agente roda o loop dele → juiz → consentimento → ela lê e decide de novo).

### Erro meu, registrado

Afirmei que `MYSTIQUE_EFFORT=xhigh` estava no Dokploy e era a causa da lentidão. **Não estava setado**
— o código não mandava `reasoning_effort` nenhum. Conferi no `docker inspect` do container só depois
que o Henrique corrigiu. Verificar antes de afirmar.

---

## 2. PENDENTE — pedido do Henrique, não iniciado

### 2.1 Auth0 + chave do próprio usuário (o item grande)

- Login/cadastro **só por passkey**, inclusive recuperação
- Guardar a chave de API do usuário (OpenRouter, ou DeepSeek) com segurança — avaliar **Auth0 Token Vault**
- **Testar de verdade** que uma chave guardada lá funciona
- **Live** exige conta; **Replay guiado NÃO exige** e continua aberto
- Disclaimers de **LGPD e cookies**
- Memória da Mystique **persistente por conta**
- Tela de cadastro de API mostrando os endpoints/opções que o OpenRouter oferece

**Avaliação honesta de escopo:** é fluxo de autenticação novo + sessão no backend + storage de
credencial + gating da UI. São horas, não minutos. Fazer por partes, nesta ordem:
passkey → sessão → cofre da chave → gating do Live → persistência por conta.

### 2.2 Os 3 primeiros cards ainda quebram

`agente-coordenador-cuidadores`, `agente-filho-cuidador`, `agente-pos-consulta`.
Já apliquei defaults defensivos em `rosterAgents` (`f927683`) e **não resolveu**. A causa real ainda
não foi isolada — **é preciso ver o erro de console, não deduzir.**

### 2.3 Replay guiado — UI ruim

Itens sobrepostos. A barra "Mystique (bem)" precisa ficar melhor e **expansível no clique**.

### 2.4 Registrado, a NÃO fazer agora (decisão do Henrique)

Fluxo de adicionar agentes de fora para fazer uma espécie de **destilação**. Demora demais agora.
Fica anotado como direção futura.

---

## 3. Playwright — armadilha que custou tempo

`page.goto(..., { waitUntil: 'networkidle' })` **nunca resolve** nesta app: o stream AG-UI
(`/agui/stream`) mantém a conexão aberta de propósito, então a rede nunca fica ociosa.

**Use `waitUntil: 'domcontentloaded'`** e depois espere por um seletor concreto.
O Playwright 1.59.1 está instalado em `/tmp/pw` (fora do repo).

---

## 4. Como fazer deploy (funcionou 6× hoje)

1. Editar, commitar como `henrique-simoes <simoeshz@gmail.com>`, `git push origin main`
2. Henrique clica **Redeploy** no Dokploy (a extensão do Chrome não conecta daqui, então o clique é dele)
3. Conferir: `ssh root@2.24.66.167 'git -C /etc/dokploy/compose/mystique-fe5rwp/code rev-parse HEAD'`
4. `Cmd+Shift+R` no navegador — o CSS fica em cache

Nunca rodar `docker compose` na mão: não entra no histórico e o próximo deploy sobrescreve.
