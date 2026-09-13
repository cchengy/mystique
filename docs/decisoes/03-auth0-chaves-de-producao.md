# Conexões sociais do Auth0 com credenciais próprias

Status: aceito para `post-hackathon`. Ação do operador do tenant, não do código.

## Contexto

Login social é uma escolha de produto: fica. O que não pode ficar são as **development
keys** do Auth0, que o Dashboard aponta:

> **Dev Keys** — One or more of your connections are currently using Auth0 development
> keys and should not be used in production.

São credenciais OAuth **compartilhadas**, mantidas pelo Auth0 e usadas por qualquer tenant
que ainda não cadastrou as suas. Em produção elas trazem:

- tela de consentimento em nome do Auth0, não da Mystique — o usuário autoriza um app que
  não é o nosso, o que é exatamente o oposto do que o resto deste produto promete;
- rate limits e revogações compartilhados com terceiros desconhecidos;
- o próprio Auth0 declara que não devem ser usadas em produção;
- **o risco sério aqui:** trocar as credenciais depois pode mudar o `sub` do usuário. O
  `sub` é a identidade da conta na Mystique — chave do workspace, do Reasoning Bank, das
  sessões e das credenciais no cofre. Trocar depois de ter usuários desvincula pessoas dos
  seus próprios dados.

## Decisão

Manter as conexões sociais desejadas e **registrar credenciais próprias em cada uma**,
antes de haver usuários reais. Não desabilitar login social.

Para cada provedor (Google como exemplo):

1. No provedor, criar um OAuth Client próprio (Google Cloud Console → APIs & Services →
   Credentials → OAuth client ID, tipo *Web application*).
2. Authorized redirect URI: `https://<seu-tenant>.auth0.com/login/callback`
   (o domínio do tenant configurado em `AUTH0_DOMAIN`).
3. Authorized JavaScript origin: `https://mystique.2-24-66-167.sslip.io`.
4. No Auth0: Authentication → Social → *a conexão* → colar **Client ID** e **Client
   Secret**, salvar. O aviso de dev keys some dessa conexão.
5. Em Applications → *a aplicação da Mystique* → Connections, confirmar que só ficam
   habilitadas conexões com credenciais próprias e a conexão de banco/passkey.

O Client Secret é digitado pelo dono do tenant na UI do Auth0. Não entra em repositório,
Compose, `.env`, log, chat ou histórico de shell — mesma regra do `MYSTIQUE_VAULT_KEY`
([`02-cofre-byok-24h.md`](02-cofre-byok-24h.md)).

## Ordem importa

Fazer isso **antes** de divulgar o produto. Depois de existirem contas, trocar as
credenciais de uma conexão social exige planejar migração de identidade (Account Linking
ou mapeamento explícito de `sub` antigo → novo); não existe caminho automático.

## Verificação

- O alerta "Dev Keys" desaparece do Dashboard.
- A tela de consentimento do provedor mostra o nome da aplicação da Mystique.
- Um login completo devolve um access token com a `audience` da API, e o `sub` de uma conta
  existente continua o mesmo (checar em Applications → APIs → logs, ou entrando com uma
  conta de teste e vendo que as conversas continuam lá).

## Fora de escopo

Nada disso muda o código. `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID` e `AUTH0_AUDIENCE` seguem
iguais; a aplicação só verifica o JWT contra o JWKS do tenant
([`01-auth0-e-chave-do-usuario.md`](01-auth0-e-chave-do-usuario.md)). O processo de login
seguro já implementado — passkey pelo Universal Login, token verificado no servidor, `sub`
como única identidade, credenciais de provedor isoladas no cofre — permanece exatamente
como está.
