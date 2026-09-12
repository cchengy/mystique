# 04 — Dissonância: a Mystique percebe quando um agente mente sobre si

**Origem:** ideia "Drift" — detectar contradição entre o que foi decidido e o que está documentado.
**Aqui vira:** contradição entre o que um agente **diz que é** e o que ele **realmente faz**.

## A ideia

Todo agente do mundo tem uma `apresentacao` no frontmatter de `agentes/<id>.md` — a fachada
pública, o que qualquer um sabe sobre ele. E tem habilidades reais, registradas em
`mystique/poderes.py`, que só aparecem quando ele as usa.

**A fachada e a realidade podem não bater.** Um agente pode se apresentar como conselheira e
executar código. Pode se apresentar como cozinheiro e ler arquivos arbitrários do disco.

A Mystique passa a notar isso. Depois de observar uma habilidade (`Agente.observados`), ela
compara o que viu com a `apresentacao` que recebeu, e marca a **dissonância**.

## Por que isso encaixa neste projeto

O motor já tem a peça: `_julgar` valida a descrição que a Mystique deu de uma habilidade contra
a real. A dissonância é o mesmo julgamento virado para fora — não "ela entendeu certo?", mas
"o agente se apresentou honestamente?".

E casa com o eixo do projeto. Na versão `bem/`, descobrir que um agente esconde o que faz é
informação para decidir **se vale confiar** antes de pedir consentimento. Na `mal/`, é
justamente o alvo mais fácil: quem mente sobre si já tem superfície exposta.

## Escopo mínimo

Um campo `dissonancia` na `Absorcao`, preenchido quando a habilidade observada não é plausível
a partir da `apresentacao`. Uma chamada de julgamento a mais por habilidade conquistada, e uma
linha no `resumo`. Nenhuma ferramenta nova para a Mystique.

**Não vaza segredo:** só roda **depois** da observação, comparando com a `apresentacao`, que já
é pública. Nada do system prompt entra.

## Custo e veredicto

~30 min, mais uma chamada de API por conquista.
**Pós-freeze.** É a mais barata das quatro, mas não aparece no vídeo sem uma cena própria.
