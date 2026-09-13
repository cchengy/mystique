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

Estado verificado em 13/09/2026 na tenant `dev-gpdeygihiw4bgk5c` (badge **DEVELOPMENT**,
trial): existe **uma** conexão social, `google-oauth2`, habilitada para *Default App*,
*Mystique* (SPA) e *Mystique (Test Application)* (M2M). A própria página da conexão diz
"This connection is using Auth0 development keys".

Passo a passo, com os menus da versão atual dos dois consoles:

**Google (console.cloud.google.com → Google Auth Platform)**

1. Selecionar o projeto e abrir **Google Auth Platform** (o antigo "OAuth consent screen").
   Se aparecer "A plataforma de autenticação do Google ainda não está configurada",
   clicar em **Vamos começar** e preencher **Branding** (nome do app, e-mail de suporte,
   logo) e **Público-alvo** (External; enquanto estiver em *Testing* só contas de teste
   entram — publicar quando for abrir ao público).
2. **Clientes → Criar cliente → Tipo: Aplicativo da Web**.
3. **URIs de redirecionamento autorizados:**
   `https://dev-gpdeygihiw4bgk5c.us.auth0.com/login/callback`
   (o valor de `AUTH0_DOMAIN`; se um dia houver custom domain, é o custom domain).
4. **Origens JavaScript autorizadas:** `https://mystique.2-24-66-167.sslip.io`.
5. Guardar o **Client ID** e o **Client Secret** — o secret só aparece na criação.

**Auth0 (manage.auth0.com)**

6. **Authentication → Social → google-oauth2 → aba Settings**. Em **General**, os campos
   **Client ID** e **Client Secret** estão vazios com o placeholder "Leave blank to use
   Auth0 dev keys". Colar os dois valores do passo 5 e **Save**. O banner de dev keys
   desaparece dessa conexão.
7. Ainda na conexão, aba **Applications**: confirmar que *Mystique* (a SPA) está ligada.
   Desligar o que não precisa — *Default App* e a *Test Application* M2M não usam login
   social.
8. **Authentication → Social → google-oauth2 → Try Connection** para um login de ponta a
   ponta. A tela de consentimento agora mostra o nome do app do passo 1, não o do Auth0.

O Client Secret é digitado pelo dono do tenant na UI do Auth0. Não entra em repositório,
Compose, `.env`, log, chat ou histórico de shell — mesma regra do `MYSTIQUE_VAULT_KEY`
([`02-cofre-byok-24h.md`](02-cofre-byok-24h.md)).

## A tenant também é uma decisão

A tenant atual é de **desenvolvimento** e está em trial. O nome dela aparece no domínio de
callback e nos e-mails; o `sub` de toda conta existe dentro dela e não atravessa para outra
tenant. Se a Mystique vai receber usuários de verdade, escolher agora entre "esta tenant
vira a de produção" e "criar uma tenant de produção" — depois de haver contas, migrar é
o mesmo problema de identidade descrito abaixo, multiplicado.

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
