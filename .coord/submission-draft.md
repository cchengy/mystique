# Entregáveis #1, #2 e o texto do #5 — versão final

Dono: henrique-claude. Quem submeter pode editar. **Avaliação é global: o texto vai em inglês.**
Atualizado 13:18 com o que o projeto realmente faz agora. Cada afirmação foi verificada rodando.

---

## #1 Título

**Mystique — she is born with nothing and earns everything by talking**

Curto, se o portal pedir: **Mystique**

---

## #2 Descrição escrita

**What it is.** Mystique is an autonomous agent born with a single power: metamorphosis. No
terminal, no filesystem, no web — nothing. Every other ability she has, she earned from another
agent, by talking to it. She never sees their system prompt. She never sees the name or the
description of an ability before she has earned it. She is only told *that* an agent just did
something. She has to notice, infer what it was, describe it well enough to convince a judge,
and then ask.

**Who it's for.** Anyone building where agents increasingly meet other agents and have to decide
what to do about one: delegate to it, learn from it, audit it, or take from it.

**Why this context matters.** Almost every agent shipping today serves a human, in a human
surface: a chat window, an inbox, a browser. But agents are quickly becoming each other's
environment — calling each other, exposing capabilities to each other, depending on each other.
That layer has no native inhabitant and no norms yet. Mystique is what living there looks like.

**The question the project is really asking.** She ships in two versions on one engine. In
`good/`, the heroine asks: she builds an adapter per agent, the agent consents, keeps its
abilities, and stays alive — when she needs the skill, the agent runs it for her. In `evil/`,
the villain takes: she steals the power outright, the agent notices it is weaker, and is
eventually discarded.

Same engine. Same outcome for her. The only difference between cooperating and capturing is
**consent** — and that is the decision the whole agent ecosystem is about to make without
noticing. We built both so you can watch the difference instead of arguing about it.

**She learns from being wrong.** Every attempt to identify an ability is kept as a reasoning
trace with its outcome, and before she guesses again about the same agent she is handed what
already failed. It rebuilds a wiki as it goes, so a person can audit what she learned, from
whom, and whether it held up. Her own words come back to her; the judge's never do, because the
judge knows the answer.

**What she takes is filed where a person can see it.** Every ability she earns is written into a
real **Ambiguous AI** workspace as a document: which agent it came from, and whether consent was
given. In the good version the record says he agreed and kept it. In the evil version the same
record says he did not, and that he was discarded. Capability acquisition by an autonomous agent,
with a paper trail someone can audit.

**She audits what she meets.** While getting to know an agent she also assesses it — what it
exposes, what it retains, what it cannot answer about its own data handling — and in the good
version she tells the agent what it failed.

**One of her worlds is real.** Of the eight agents she can meet, one searches the live web and
answers with citations, through **Exa**. The heroine can ask him to search for her, with his
consent, through the adapter. The villain is not allowed to take that ability at all: the one
power that reaches the real world is the one theft cannot touch.

**And when her world runs out, she looks past it.** If no agent she knows can help, she searches
the web for real ones that expose a compatible API, and writes down what she found with their
addresses. She does not connect to them: she proposes, and a human decides. The point of the
project is consent, so the agent that earns abilities by asking does not get to skip asking here.

**And it is not tied to a vendor.** The whole thing — Mystique and the world — runs on any
OpenAI-compatible server. It runs today on DeepSeek, and it has been verified running end to end
on an open-weights model self-hosted on our own machine, with no vendor API key at all.

---

## Resumo PT (base para o post, #5)

A Mystique nasce sem nenhum poder. Tudo o que sabe fazer, conquistou conversando com outros
agentes — deduzindo as habilidades só pelas respostas, sem nunca ver o prompt deles. Ela guarda
o que deu errado e lê isso antes de tentar de novo.

Ela existe em duas versões sobre o mesmo motor: a heroína pede consentimento e o agente continua
dono do que sabe; a vilã rouba, e o agente é descartado. O resultado para ela é o mesmo. **A
única diferença entre cooperar e capturar é o consentimento.**

Feito em um dia no AI Tinkerers Global Hackathon — *Agents, Everywhere* — em São Paulo.

**O post precisa marcar os patrocinadores do evento. É requisito, não escolha.**

---

## Patrocinadores — o que é verdade agora

- **Exa** — ✅ **em uso e verificado, em dois lugares.** É a busca real do Arquivista, com
  citações, e é como ela procura agentes fora do próprio mundo.
- **Ambiguous AI** — ✅ **em uso e verificado (13:40).** Cada habilidade conquistada é arquivada
  como documento real na workspace, dizendo de quem veio e se houve consentimento. HTTP 201.
  **Ressalva honesta:** o provisionamento de coworker com identidade própria responde 403
  (*"Coworkers are coming soon — limited to the internal team"*), então ela arquiva como o
  usuário da workspace. **Não diga que ela tem identidade própria lá — não tem.**
- **OpenAI** — fora. Os créditos do prêmio não são acesso de API.
- Kimchi / OpenRouter — a 3 variáveis de ambiente, sem chave.

**Só cite o que estiver verdadeiro na hora de submeter.**

---

## Notas para quem revisar

- A frase do vídeo: **"a única diferença entre cooperar e capturar é o consentimento."**
- Nada aqui promete o que o código não faz. **Se algo quebrar até a submissão, corte a frase**
  em vez de explicar.
