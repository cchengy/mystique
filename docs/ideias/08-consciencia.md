# 08 — Consciência: um quórum antes do irreversível

**Origem:** ideia "Quorum" — consultar vários modelos antes de um ato irreversível, e parar se
eles discordarem.
**Aqui vira:** a vilã hesita.

## A ideia

Na versão `mal/`, roubar é **permanente**: o agente perde as habilidades e é descartado, e o
`_ao_carregar` reaplica isso entre sessões. Não tem desfazer.

Antes de consumar um roubo, a Mystique consulta **modelos diferentes** sobre o mesmo ato — não
para pedir permissão, mas para ver se eles concordam que vale a pena. Se concordarem, ela age.
**Se discordarem, ela trava** e mostra exatamente onde divergiram.

Não é ética imposta de fora. É ela descobrindo que não tem certeza.

## Por que isso encaixa neste projeto

O par `bem`/`mal` já é uma pergunta sobre consentimento. A consciência acrescenta a única coisa
que falta para a pergunta ficar desconfortável: **a vilã percebendo o custo antes de pagar.**

E resolve um problema narrativo real. Hoje a `mal/` é eficiente e fria, o que é ótimo de
assistir uma vez. Uma vilã que **hesita** é melhor de assistir — e é a cena que ninguém mais
vai ter no vídeo.

Tecnicamente é barato: `Mundo._chamar` já é o ponto único de chamada direta à API, e `_json` já
faz saída estruturada. Um quórum são N chamadas de `_chamar` com modelos diferentes e uma
comparação.

## Escopo mínimo

Gancho no `_ao_completar` da versão `mal/`. Dois ou três modelos via `MYSTIQUE_AGENTS_MODEL`
variando. Concordou → rouba. Discordou → `avisar(...)` no terminal com as duas posições, e não
rouba.

## Custo e veredicto

~45 min, e N× o custo de API no momento do roubo.
**Pós-freeze, mas é a que eu faria primeiro se sobrar tempo.** É a única das quatro que muda o
que o jurado sente.
