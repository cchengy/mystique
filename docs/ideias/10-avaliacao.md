# 10 — Avaliação: o que ela conquistou presta?

**Origem:** ideia de "performance review" — playbooks versionados, revisão do que um agente fez,
um humano responsável.
**Aqui vira:** revisar as conquistas da Mystique, e versionar o que ela aprendeu.

## A ideia

A `Absorcao` já é persistida em `<versão>/workspace/<PASTA>/<id>.json` e sobrevive entre
sessões. Hoje ela é um registro morto: guarda o que foi conquistado, e ninguém pergunta se
aquilo ficou **bom**.

A avaliação acrescenta três coisas:

1. **Nota de conquista.** Depois de usar uma habilidade conquistada (`usar_adapter` ou
   `usar_poder`), registrar se funcionou. Uma habilidade roubada que ela não sabe usar direito é
   um dado, não um fracasso.
2. **Versão com motivo.** Quando ela refina o entendimento de uma habilidade, gravar a versão
   nova **com o motivo da mudança** — "na primeira tentativa eu achava que era só receita; era
   escalar porção também".
3. **Um humano responsável.** Quem rodou aquela instância. O `workspace/` é local de cada um, e
   na arquitetura assíncrona que o time descreveu cada pessoa roda a sua Mystique.

## Por que isso encaixa neste projeto

É o que transforma o `workspace/` de cache em **memória com história**. A Mystique deixa de ter
só uma lista do que pegou, e passa a ter a trajetória de como foi entendendo — que é
exatamente a diferença entre copiar uma habilidade e aprender uma.

E encaixa direto na ideia que o time já teve de várias instâncias assíncronas: se cada pessoa
roda a sua e o repositório é a memória comum, a avaliação é o que permite juntar aprendizado de
instâncias diferentes sem virar bagunça.

## Escopo mínimo

Dois campos na `Absorcao` — `tentativas` e `motivo_da_versao` — e o `resumo` mostrando os dois.
Sem endpoint, sem UI.

## Custo e veredicto

~40 min para a versão mínima. **Pós-freeze**, e a menos visível das quatro num vídeo de dois
minutos: o valor dela aparece na segunda e na terceira sessão, não na primeira.
