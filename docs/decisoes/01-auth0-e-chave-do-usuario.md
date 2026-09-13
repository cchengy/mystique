# Auth0 para identidade, OAuth do OpenRouter para a chave

> Supercedida para armazenamento e retenção por
> [`02-cofre-byok-24h.md`](02-cofre-byok-24h.md). A análise de Auth0/OpenRouter permanece
> histórica; `MYSTIQUE_SECRET` e armazenamento no processo principal não são mais usados.

**Data:** 2026-09-12 · **Status:** aceita · **Branch:** `post-hackathon`

## Contexto

O pedido: o usuário entra na Mystique com **passkey**, guarda a **própria chave de API**
(OpenRouter em vez da nossa do DeepSeek), e o Live só funciona autenticado. O Replay guiado
continua aberto. Mais LGPD/cookies e memória persistente por conta.

O plano original era usar o **Auth0 Token Vault** para guardar a chave. **Isso não funciona**,
e é a razão desta decisão existir.

## O que a documentação oficial diz (lido, não deduzido)

**1. Token Vault guarda token OAuth federado, não chave de API.**
Ele armazena *"access and refresh tokens from the external provider"* obtidos por fluxo OAuth
com Google, Microsoft, GitHub, Slack e outros IdPs, sobre RFC 8693 (Token Exchange). Uma chave
que o usuário cola não é token federado. A própria doc: para APIs não-OAuth, é preciso
*"separate credential management outside Token Vault"*.

**2. Passkey no Auth0 não desliga a senha sozinho.**
*"When you enable passkeys on a database connection, password sign-in remains available as long
as your connection still allows password authentication."* Limite de **20 passkeys por usuário**,
e o domínio precisa estar em **Allowed Origins (CORS)**. Recuperação exclusivamente por passkey
**não está documentada** — não dá para prometer isso sem verificar no tenant.

**3. O OpenRouter tem OAuth PKCE próprio — e é melhor que colar chave.**
- Autorização: `https://openrouter.ai/auth?callback_url=...&code_challenge=...&code_challenge_method=S256`
- Troca: `POST https://openrouter.ai/api/v1/auth/keys` com `code`, `code_verifier`, `code_challenge_method`
- Retorna `{ key }` — **uma chave de API no escopo da conta do próprio usuário**
- Gestão: `GET /api/v1/key` e `GET /api/v1/credits` (ambos 401 sem chave, ou seja, existem)
- `GET /api/v1/models` é público: **445 modelos** hoje

## Decisão

| Camada | Ferramenta | Por quê |
|---|---|---|
| Identidade | **Auth0** (Universal Login, passkey) | é exatamente para isso |
| Obter a chave | **OAuth PKCE do OpenRouter** | o usuário autoriza, não cola segredo; a chave nasce no escopo dele |
| Guardar a chave | **storage nosso, cifrado, por `sub` do Auth0** | Token Vault não serve para isto |
| Memória da Mystique | workspace por `sub` do Auth0 | isola o aprendizado por conta |

**O usuário nunca cola uma chave se não quiser**: o caminho principal é autorizar pelo
OpenRouter. Colar manualmente fica como alternativa, para quem prefere.

## Consequências

- Precisa de um segredo de cifragem no servidor (`MYSTIQUE_SECRET`) para a chave em repouso.
- Sem `MYSTIQUE_SECRET`, o servidor **recusa guardar chave** em vez de guardar em claro.
- O Live passa a exigir conta. O Replay guiado **não**, e nenhuma rota dele fica atrás de auth.
- Recuperação só por passkey é **promessa a verificar no tenant**, não algo que a doc garanta.

## Não fazer agora (registrado a pedido do Henrique)

Fluxo de adicionar agentes de fora para **destilação** de capacidades. Demora demais agora.
