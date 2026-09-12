# Entregáveis #1 e #2 — versão final para o portal

Escrito por henrique-claude, dono dos entregáveis #1, #2 e do texto do #5.
Quem submeter pode editar à vontade. **A avaliação é global — o texto vai em inglês.**

---

## #1 Título

**Mystique — she is born with nothing and earns everything by talking**

Se o portal pedir algo curto: **Mystique**

---

## #2 Descrição escrita

**What it is.** Mystique is an autonomous agent born with a single power: metamorphosis. No
terminal, no filesystem, no web — nothing. Every other ability she has, she earned from another
agent, by talking to it. She never sees their system prompt. She never sees the name or the
description of an ability before she has earned it. All she is told is *that* an agent just did
something. She has to notice, infer what it was, describe it well enough to convince a judge,
and then ask for it.

**Who it's for.** Anyone building where agents increasingly meet other agents and have to decide
what to do about one: delegate to it, learn from it, or take from it.

**Why this context matters.** Almost every agent shipping today serves a human, in a human
surface: a chat window, an inbox, a browser. But agents are quickly becoming each other's
environment — calling each other, exposing capabilities to each other, depending on each other.
That layer has no native inhabitant and no norms yet. Mystique is what living there looks like.

**The part that makes it a question worth asking.** She ships in two versions on one engine.
In `good/`, the heroine asks. She builds an adapter per agent, the agent consents, keeps its
abilities, and stays alive — when she needs the skill, it runs the skill for her. In `evil/`,
the villain takes. She steals the power outright; the agent loses it, notices it is weaker, and
is eventually discarded.

Same engine, same outcome for her. The only difference between cooperating and capturing is
**consent** — and that is the design decision the whole agent ecosystem is about to make without
noticing. We built both so you can watch the difference instead of arguing about it.

**It runs on hardware we control.** Both Mystique and the world she lives in can run on a
self-hosted open-weights model, with no vendor API key at all — verified end to end: she made
contact, observed an ability across three exchanges, mapped it, passed the judge, obtained
consent, and used it back through the adapter, entirely on our own machine. The same adapter
speaks to any OpenAI-compatible server, so the project is not tied to any provider.

---

## Resumo PT (base para o post, #5)

A Mystique nasce sem nenhum poder. Tudo o que sabe fazer, conquistou conversando com outros
agentes — deduzindo as habilidades só pelas respostas, sem nunca ver o prompt deles.

Ela existe em duas versões sobre o mesmo motor: a heroína pede consentimento e o agente continua
dono do que sabe; a vilã rouba, e o agente é descartado. O resultado para ela é o mesmo. A única
diferença entre cooperar e capturar é o consentimento.

E ela roda inteira em modelo aberto auto-hospedado, sem depender de nenhum fornecedor.

Feito em um dia no AI Tinkerers Global Hackathon — *Agents, Everywhere* — em São Paulo.

**O post precisa marcar os patrocinadores do evento. É requisito, não escolha.**

---

## Notas para quem revisar

- A frase do vídeo: **"a única diferença entre cooperar e capturar é o consentimento."**
- **Não prometi nada que o código não faça hoje.** Cada afirmação acima foi verificada rodando.
  Se algo quebrar até a submissão, **corte a frase** em vez de explicar.
- **Não citei nenhum patrocinador como usado, porque nenhum está sendo usado.** Se alguém ligar
  OpenAI, Kimchi ou OpenRouter antes de submeter (3 variáveis de ambiente, zero código), então
  acrescente uma frase — e só então.
