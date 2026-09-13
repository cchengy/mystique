# Cofre BYOK isolado com retenção de 24 horas

Status: aceito para `post-hackathon`.

## Decisão

Mystique roda em um VPS padrão da Hostinger, sem TEE, enclave ou atestação remota. Por
isso o produto **não promete zero-knowledge** nem proteção contra root, Docker daemon,
Dokploy ou operador do host. A mitigação adotada é defesa em profundidade:

- um container `credential-broker` é o único processo que monta o volume de credenciais
  e recebe `MYSTIQUE_VAULT_KEY`;
- OpenRouter, Exa e todo provedor futuro são BYOK;
- cada segredo é cifrado individualmente com AES-256-GCM, nonce aleatório e AAD que
  vincula versão, conta Auth0 e provedor;
- o broker verifica o access token Auth0 diretamente antes de acessar uma credencial;
- a aplicação usa proxies internos do broker e não recebe o segredo de volta;
- o proxy aceita somente `chat/completions`, leitura de chave/créditos e as operações
  Exa necessárias; outros caminhos e corpos acima de 2 MiB falham fechados;
- a credencial expira exatamente 24 horas depois de conectada. Login e uso não renovam o
  prazo. A limpeza roda no início e a cada hora; o acesso também falha fechado e remove
  registros vencidos;
- chaves nunca entram em logs, URLs, Compose, imagem, repositório ou environment do
  container principal.

O formulário web ainda atravessa o processo principal uma vez quando o usuário cola uma
chave ou retorna do OAuth. Isso é uma limitação explícita do frontend servido pelo mesmo
host. O broker reduz persistência e blast radius, mas um comprometimento do host ou da
aplicação no momento da conexão ainda pode capturar o segredo.

## Retenções diferentes

- **Credenciais de provedores:** 24 horas desde a conexão, sem extensão automática.
- **Sessões, conversas, Reasoning Bank, perfis, adaptações, auditorias e preferências:**
  60 dias desde o último uso autenticado. O prazo é gravado a partir de `auth_time`/`iat`
  do access token, então a renovação silenciosa do Auth0 também o move: na prática é
  inatividade, não "último login". A UI diz exatamente isso — ver
  [`docs/auditorias/2026-09-13-learning-and-accounts.md`](../auditorias/2026-09-13-learning-and-accounts.md), item 9.
- **Exclusão manual:** apaga imediatamente credenciais e todos os dados da aplicação.
  A identidade Auth0 continua separada, salvo integração futura explícita com a
  Management API.

Esses dados de 60 dias ficam em um volume privado com permissões de processo, mas não são
zero-knowledge nem cifrados com uma chave exclusiva do usuário. O operador root continua
dentro do modelo de confiança. A UI deve dizer isso sem sugerir que Auth0 cifra o volume.

## Topologia mínima

`mystique` e `credential-broker` compartilham apenas uma bridge interna `vault-link`.
Cada serviço recebe sua própria bridge de egress. O broker não publica portas, não monta
workspaces, roda sem capabilities, sem privilégios, com filesystem raiz read-only e tmpfs
restrito. O container principal não monta `mystique-credentials`.

## Operação e rotação

`MYSTIQUE_VAULT_KEY` deve ser um valor base64url aleatório de 32 bytes configurado somente
no serviço do broker pelo Dokploy. Rotacionar essa chave invalida imediatamente todas as
credenciais existentes; não existe fallback nem recuperação. Gere fora de logs e shell
history, por exemplo pela UI segura de secrets do operador.

Durante a migração, se `MYSTIQUE_VAULT_KEY` ainda não existir, somente o broker recebe o
antigo `MYSTIQUE_SECRET` e deriva dele uma chave de 32 bytes com SHA-256 e separação de
domínio. O processo principal não recebe nenhum dos dois. Depois da primeira rotação segura,
remova o fallback legado; credenciais antigas podem expirar naturalmente em no máximo 24h.

O Compose de produção define `MYSTIQUE_REQUIRE_AUTH=true`: se Auth0 estiver incompleto, a
aplicação não inicia. Nenhuma chave global de modelo é injetada no processo principal.

## Propriedade do volume de credenciais

O broker roda sem privilégios (uid 999) e com filesystem raiz read-only. Um volume Docker
novo nasce de root e 0755, então **toda** escrita de credencial falhava com `EACCES`: o
usuário voltava do OAuth do OpenRouter e nada acontecia, porque o erro virava um 500 que o
frontend engolia. O serviço `vault-init` do Compose faz `chown 999:999` e `chmod 700` no
volume antes do broker subir, e `cofre._write` agora responde 503 com texto legível em vez
de estourar uma traceback. `vault-init` não recebe `MYSTIQUE_VAULT_KEY` e roda sem rede.

## Gates de release

Antes de deploy: provar expiração e purge em 24 horas, adulteração fail-closed, separação
por `sub`, ausência do segredo no volume/environment da aplicação, autenticação própria do
broker, exclusão manual e de 60 dias, Compose sem porta publicada pelo broker, testes/build
verdes e inspeção visual do onboarding em light/dark e desktop/mobile.
