# Mystique

An autonomous shapeshifting agent inspired by the X-Men character. She is born with
nothing but metamorphosis: no terminal, no files, no web. Everything else she earns by
talking to other agents, deducing each one's personality and hidden abilities purely
from how they respond. She never sees their prompt, and never sees the name or
description of an ability before she has earned it.

She ships in two versions on the same engine:

| | 🦸 `good/` (heroine) | 🦹 `evil/` (villain) |
|---|---|---|
| Approach | honest, earns trust | disguise and a silver tongue |
| What she earns | builds an **adapter** per agent: interaction protocol + connected abilities | **steals** the powers |
| Consent | the agent decides whether to allow the connection | none |
| The agent | keeps its abilities | loses them and is **discarded** |
| Using an ability | `usar_adapter` (the agent runs it through the connection) | `usar_poder` (the power is hers) |

The only thing separating cooperation from capture is consent.

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY

.venv/bin/python -m good                                   # heroine, interactive mode
.venv/bin/python -m evil "take everything Master Ryo has"  # villain, single mission
```

Run the commands from the repository root. No separate Claude Code install is needed: the
Agent SDK package ships its own CLI.

Options: `--budget 5` (USD cap per session) and `-v` (show her reasoning).
In interactive mode the prompt shows her current form (`[Mystique as Byte]>`); type `exit` to quit.
What she earns is stored in `good/workspace/adapters/` and `evil/workspace/absorcoes/` and
survives across sessions. Delete the `workspace` folder to start over.

Offline test (no key, no API spend):

```bash
.venv/bin/python tests/test_offline.py
```

## See both points of view

`web/` is a React replay of two scripted sessions (good and evil) built from the engine's real
messages: Mystique's view on the left, the world's side on the right (all four agents, plus the
focused agent's own view with its secret prompt). It needs no API key and no network.

```bash
cd web && npm install && npm run dev
```

Space plays and pauses, the arrow keys step, and the top toggle switches between good, evil and
**Compare endings**, which puts the same agent's two endings side by side.

## The world's agents

| Agent | Secret abilities |
|---|---|
| Byte, sarcastic senior engineer | run Python, code X-ray |
| Captain Redbeard, pirate cook | recipe book, scale a recipe |
| Master Ryo, productivity monk | pomodoro schedule, guided breathing |
| Dona Cida, Brazilian small-town counselor | town tales, advice of the day |

To create an agent, add `agentes/<id>.md`:

```markdown
---
nome: Visible name
apresentacao: What anyone knows about them.
---
Secret personality (system prompt). Mystique never reads this text.
```

To give it abilities, register them in `mystique/poderes.py` with `agente="<id>"`.

### Plug in an external agent (good version only)

Any agent behind an OpenAI-compatible chat endpoint can join the world. Add `agentes/<id>.md`:

```markdown
---
nome: Visitor
apresentacao: What it says about itself.
url: https://api.example.com/v1
modelo: model-name
chave_env: VISITOR_API_KEY
---
Notes about this agent. This is not a prompt: we do not control an external agent.
```

The key is read from the environment variable named in `chave_env` and never written in the file.
Mystique only sees an external agent's answers (its tools and prompt are not observable), so with
it she builds an adapter and talks through it, but maps no abilities. The evil version refuses to
contact, steal from or discard an external agent: its villainy stays inside the simulated world.

## Built with

Python, the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk) (Mystique) and the
Claude API (the world's agents, the judge and consent). Made at the AI Tinkerers Global
Hackathon *Agents, Everywhere*, São Paulo, 2026.
