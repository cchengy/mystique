# Conexões do Auth0 em produção: sem chaves de desenvolvimento

Status: aceito para `post-hackathon`. Ação do operador do tenant, não do código.

## Problema

Ao abrir o login, o Dashboard do Auth0 mostra:

> **Dev Keys** — One or more of your connections are currently using Auth0 development
> keys and should not be used in production.

As *development keys* são credenciais OAuth **compartilhadas**, mantidas pelo Auth0 e
usadas por qualquer tenant que ainda não cadastrou as suas. Elas existem para testes e
carregam limites reais em produção:

- a tela de consentimento do provedor aparece em nome do Auth0, não da Mystique;
- não há isolamento nem quota próprios: rate limits e revogações são compartilhados;
- o Auth0 declara explicitamente que não devem ser usadas em produção;
- o `sub` do usuário pode mudar quando as credenciais são trocadas depois — e o `sub` é a
  identidade da conta na Mystique, a chave de todo dado do usuário e do cofre.

O último item é o mais sério aqui: trocar as chaves depois pode desvincular contas
existentes dos seus dados. Resolver antes de ter usuários reais é muito mais barato.

## Decisão

O login da Mystique é **passkey primeiro**. Portanto:

1. **Preferido:** desabilitar as conexões sociais na aplicação (Auth0 Dashboard →
   Applications → *a aplicação da Mystique* → Connections) e manter apenas a conexão de
   banco/passkey. Sem conexão social não há dev keys, e o alerta desaparece.
2. **Se uma conexão social for desejada** (Google, GitHub, …): registrar as credenciais
   próprias no provedor e cadastrá-las na conexão do Auth0
   (Authentication → Social → *a conexão* → Client ID / Client Secret), com o callback
   `https://<tenant>/login/callback`. Só então habilitar a conexão na aplicação.

Nunca deixar uma conexão com dev keys habilitada na aplicação de produção.

## Verificação

- O alerta "Dev Keys" some do Dashboard.
- Em Applications → Connections, toda conexão habilitada tem credenciais próprias ou é a
  conexão de banco/passkey.
- Um login completo continua devolvendo um access token com a `audience` da API e o mesmo
  `sub` de antes da mudança.

## Fora de escopo

Nada disso muda o código. `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID` e `AUTH0_AUDIENCE` continuam
os mesmos; a aplicação só verifica o JWT contra o JWKS do tenant
([`01-auth0-e-chave-do-usuario.md`](01-auth0-e-chave-do-usuario.md)).
