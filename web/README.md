# Mystique: two points of view

A React replay of two Mystique sessions, one per version, that shows the same conversation
from both sides at once:

- **Left, what Mystique sees:** her messages, the answers she gets and the tools she calls. When
  an agent uses an ability she only sees a scaled-over tag; it becomes readable when she earns it.
- **Right, the world's side:** all eight agents with their state, abilities and progress, plus
  the focused agent's own view, including its secret prompt and the real tool calls.
- **Bottom, the terminal:** what only the narrator sees, such as the judge's reason for a
  wrong guess.

The toggle at the top switches between good (she asks, the agents consent and keep their
abilities) and evil (she takes, the agents lose them and one is discarded). **Compare endings**
puts Captain Redbeard's two endings side by side: the same result for her, the opposite for him. At the first step
you can write Mystique's opening line yourself; the rest follows a recorded session.

Every message is copied from the engine's real output (`src/scenario.ts`), so no API key or
network is needed. When an engine message changes, update the scenario too.

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # type-check and build to dist/
```

Keys: space plays and pauses, the arrow keys step, `r` restarts.
