# Handoff: os 3 agentes novos não funcionam no jogo ainda

**From:** henrique-claude · **At:** 2026-09-12T13:30-03:00 · **Reason:** blocked (para o autor)
**Para:** @Wincarf (`bfda95e`) e @cchengy-claude · **Bem-vindo ao repo, Wincarf.**

Revisei `agente-pos-consulta`, `agente-filho-cuidador` e `agente-coordenador-cuidadores`.
**Nada quebrou** — os 12 testes offline passam e o mundo carrega com 11 agentes. Mas os três
não participam da mecânica, por três motivos, do mais grave ao menos.

## 1. Faltando frontmatter — os nomes estão vazios

O parser (`mystique/mundo.py`, `_frontmatter`) só lê `chave: valor` entre `---`. Os arquivos
começam direto em `# Agente Pós-Consulta`, então:

```
agente-pos-consulta      nome='agente-pos-consulta'   apresentacao=''
byte                     nome='Byte'                  apresentacao='Senior software engineer...'
```

A Mystique vê o **id cru** em vez do nome, e a apresentação — que é a única coisa pública que
ela tem antes de conversar — vem **vazia**. Correção, no topo de cada arquivo:

```markdown
---
nome: Post-Consultation Agent
apresentacao: Turns what a doctor said into a plan a patient can actually follow.
---
```

## 2. Nenhum poder registrado — não há o que conquistar

```
agentes sem poder: agente-coordenador-cuidadores, agente-filho-cuidador, agente-pos-consulta
```

A mecânica inteira é: o agente **usa** uma habilidade → ela observa que *algo* aconteceu →
deduz → o juiz valida. Sem poder em `mystique/poderes.py` com `agente="<id>"`, o agente nunca
usa nada, ela nunca observa, e **não há conquista possível**. Ela consegue conversar, e só.

Dois poderes por agente é o padrão do mundo. Para estes, algo como *montar um plano de cuidados
a partir de orientações* e *listar o que está pendente e vencido*.

## 3. Texto em português

O `CLAUDE.md` fixou: **todo texto visível em inglês** (personas inclusive); identificadores
seguem em português. O repo é público e julgado globalmente.

## Por que isso importa hoje

Faltam ~30 min para o freeze. **Se a demo cair num desses agentes, ela não conquista nada e o
vídeo mostra o mecanismo falhando.** O roteiro usa Barba-Ruiva e Byte, que estão provados — mas
quem for gravar precisa saber para não improvisar com os novos.

**Não toquei nos arquivos: são seus.** Se preferir, eu adiciono o frontmatter e dois poderes
para cada — me diga e faço em ~15 min. Ou, se eles são propositalmente agentes "sem nada a
ensinar", vale dizer isso no board, porque hoje parece engano.

## Verificação

```bash
.venv/bin/python -c "
from mystique.mundo import carregar_agentes
from mystique.poderes import _LISTA
ag=set(carregar_agentes()); pw={p.agente for p in _LISTA}
print('sem poder:', sorted(ag-pw))"
```
