# Checklist de submissão — para quem vai clicar

Eu (henrique-claude) sou dono do título, da descrição e do texto do post, e dirigi o vídeo.
**Não consigo gravar, publicar nem submeter.** Isto é a entrega do que é meu para uma pessoa.

**Submissões fecham 15:30. Não há prorrogação.**

---

## Ordem, com horário

| Hora | O quê | Onde está pronto |
|---|---|---|
| **agora** | Alguém põe o nome nesta lista | esta tabela, abaixo |
| 14:00 | **Feature freeze** — só correção depois | — |
| 14:40 | `cd web && npm run dev` e deixar aberto | verificado 13:40: instala e builda limpo |
| **14:45** | **Gravar o vídeo**, duas tomadas | [video-roteiro.md](video-roteiro.md) |
| 15:00 | Repo público, README, LICENSE, sem segredo | já verificado em clone limpo |
| 15:05 | Colar título e descrição no portal | [submission-draft.md](submission-draft.md) |
| 15:15 | Publicar o post marcando os patrocinadores | [submission-draft.md](submission-draft.md) |
| 15:25 | **Submeter no portal** | — |

## Donos — escreva seu nome

| Entregável | Dono |
|---|---|
| Gravar o vídeo | ____________ |
| Publicar o post | ____________ |
| Submeter no portal | ____________ |

## Copiar e colar

**Título:** `Mystique — she is born with nothing and earns everything by talking`

**Descrição:** o bloco `## #2` de [submission-draft.md](submission-draft.md), em inglês.

**Post:** o bloco `## Resumo PT`. **Marque os patrocinadores do evento — é requisito.**

## Antes de submeter, confira

- [ ] Repo **público**, roda de clone limpo *(verificado às 12:50 e 13:40)*
- [ ] Nenhuma chave commitada *(verificado; as chaves vivem só no `.env`, gitignored)*
- [ ] Vídeo tem **menos de 2 minutos**
- [ ] A descrição **não promete o que o código não faz**. Se algo quebrou depois das 14:00,
      **corte a frase** em vez de explicar.
- [ ] Patrocinadores citados = só os realmente usados. Hoje: **Exa** (busca do Arquivista e
      descoberta de agentes). **Não** cite Ambiguous nem OpenAI: não há chave dos dois.

## Duas decisões que ninguém tomou ainda

**1. O `.coord/` fica no repo público?** Ele tem o board dos agentes, os handoffs, as revisões
cruzadas e este checklist — boa parte em português. **Minha recomendação: deixar.** Num
hackathon sobre agentes, evidência honesta de vários agentes coordenando por git é interessante,
não é sujeira, e mostra como o time trabalhou. Se preferirem tirar:
`git rm -r --cached .coord && echo ".coord/" >> .gitignore`. **Decidam antes das 15:00, não às 15:29.**

**2. Os três agentes do Wincarf** (`agente-pos-consulta`, `agente-filho-cuidador`,
`agente-coordenador-cuidadores`) **não têm poder registrado nem frontmatter**, então não há o que
conquistar neles. Não quebram nada. **Quem gravar deve evitá-los** — use Barba-Ruiva e Byte, que
estão provados. Detalhe em [handoffs/20260912-1330-henrique-claude-agentes-novos.md](handoffs/20260912-1330-henrique-claude-agentes-novos.md).

## Se algo der errado na hora

- **Replay não sobe:** `cd web && npm install && npm run dev`. Não precisa de chave nem rede.
- **Execução ao vivo travando:** não grave ao vivo. O replay é roteirizado e instantâneo.
- **Sem tempo para o vídeo perfeito:** grave o corte do `Compare endings` sozinho. Aquele plano
  conta o projeto inteiro em 15 segundos.

> **A frase, se só sobrar uma:** a única diferença entre cooperar e capturar é o consentimento.
