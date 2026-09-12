# 09 — Roteamento: conversa é barata, julgamento é caro

**Origem:** família de ideias de roteamento de modelo (sensibilidade / custo / confiabilidade).
**Aqui vira:** a Mystique escolhendo em que modelo gastar, por tipo de trabalho.

## A ideia

Nem toda chamada deste projeto tem o mesmo valor. Hoje o `CLAUDE.md` já separa dois caminhos por
env — `MYSTIQUE_MODEL` e `MYSTIQUE_AGENTS_MODEL` — mas o segundo trata igual três coisas
muito diferentes:

| Trabalho | O que exige | Modelo |
|---|---|---|
| Agente do mundo respondendo de personagem | pouco; é conversa de personagem | **barato / peso aberto** |
| Pedido de consentimento (`bem/`) | pouco; é uma decisão sim/não | **barato** |
| `_julgar` — validar a descrição contra a habilidade real | **muito**; é o que garante a mecânica | **de ponta** |

A conversa é a maior parte do volume e a mais barata de servir. O julgamento é raro e é onde o
projeto inteiro se apoia — se o juiz errar, a Mystique conquista o que não entendeu, e o
mecanismo do segredo perde o sentido.

## Por que isso encaixa neste projeto

O time já tinha chegado nisso sozinho, na conversa gravada: *"se é mais barato interagir, ela
interage; se é mais barato assumir o papel, ela assume — e a decisão é dela."* Isto é a mesma
ideia aplicada um nível abaixo, no gasto por chamada.

Também tem um efeito prático hoje: **é a defesa contra rate limit no meio da demo.** Tirar o
volume de conversa do modelo de ponta deixa a cota onde ela importa.

## Escopo mínimo

Um terceiro env, `MYSTIQUE_JUIZ_MODEL`, com `_julgar` usando ele e o resto caindo no barato.
Três linhas em `Mundo`, mais o `.env.example`. Zero mudança de arquitetura.

## Custo e veredicto

~15 min. **É a única das quatro que eu faria antes do freeze** — corta custo, reduz risco de
rate limit ao vivo, e não toca na mecânica. Se rodar, também vira uma frase honesta no vídeo:
*"ela sabe em que vale a pena pensar caro."*
