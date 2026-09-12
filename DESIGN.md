# Mystique interface contract

## Product character

Mystique is an atmospheric, evidence-led agent workbench rather than a generic chatbot.
Density is welcome when hierarchy remains obvious. The UI must never imply that a browser
transcript is model memory, that a scripted replay is live, or that an unverified capability
was learned.

## Macrostructure and tokens

Desktop uses a workbench shell: a 280 px conversation rail, the active conversation as the
primary canvas, and agents/evidence as contextual inspection. Mobile collapses the rail into
a persistent bottom control. Colors are semantic CSS tokens (`surface`, `foreground`,
`muted`, `line`, `accent`, `loss`); both themes keep the same hierarchy. Text contrast is
4.5:1, graphical controls 3:1, focus is visible, targets are at least 24 CSS px and primary
touch targets 44 px. Spacing follows a 4 px rhythm; pills are reserved for status.

## Component contracts

- Conversation rail: create, reopen and highlight account-scoped sessions, ordered by
  recency. Long titles truncate; profile Good/Evil remains visible.
- Model drawer: visible label plus helper text says typing searches every OpenRouter model.
  Save stays disabled until the model ID changed.
- Transcript: durable user/assistant turns come from the server. Reload reconstructs them;
  ephemeral progress may stream without becoming model context.
- Composer: Enter sends, Shift+Enter inserts a line, duplicate submission is disabled, and
  disconnect errors state that nothing was sent.
- Compare: “Ela Pediu” and “Ela Tomou” show actual Good/Evil sessions and Reasoning Bank
  evidence. Frozen scenario data cannot masquerade as live history.
- Replay: visibly scripted, with restrained controls, a readable counter and no live claim.

## Dense implementation prompt

Redesign the existing React screen as a responsive agent workbench without replacing engine
semantics. Preserve real handlers and accessibility. Prove the transcript source and selected
session first. Add an account-scoped conversation rail following established Open WebUI chat
patterns: create, reopen, select and preserve context. Put OpenRouter configuration in its
footer and make model discovery explicit with a labeled searchable datalist. Correct large
buttons, noisy colors and competing hierarchy without decorative gradients or card grids.
Replace Compare's scripted ending with real Good/Evil trajectory evidence. Keep Replay
explicitly scripted and tune its hierarchy. Verify desktop/mobile, light/dark, keyboard focus
and reduced motion.

## Acceptance

At 1440×900 and 390×844 there is no horizontal overflow, clipped action or overlapping
composer. Switching sessions replaces the transcript and the next model call receives that
session's prior turns. Good/Evil state is isolated. Missing comparison evidence is labeled
honestly. Feature commits update `CLAUDE.md`; UI-contract changes update this file.
