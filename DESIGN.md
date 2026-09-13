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
- Security onboarding: disclose before login that provider credentials live for exactly
  24 hours in an encrypted, isolated broker; sessions and memory follow the 60-day rule;
  and a standard VPS cannot offer zero-knowledge against its operator. Never soften this
  into generic “secure” copy.
- Account lifecycle: show the exact deletion date, distinguish logout, Mystique-data
  deletion and Auth0-identity deletion, and require the literal confirmation phrase for
  immediate irreversible deletion. Destructive color is reserved for this boundary.
- Conversation rail: it is part of the live layout, not a reward for signing in. While the
  gate is up the rail stays on screen in a locked state — inert controls, placeholder rows
  and one line saying what sign-in unlocks. Removing it left the reserved column empty and
  the page read as broken.
- Account panel palette: the panel reads `--p-*` tokens, never the world tokens directly.
  The gate is the dark ink slab in both themes, while the same component inside the rail
  drawer sits on the world surface, which flips with the theme. Each context binds every
  token; a rule that reaches past them will look correct in one theme and be unreadable in
  the other.
- The connected state must appear on return, without a reload. The exchange is
  single-flight, so a second render pass cannot read the account before it lands and
  paint "connect a key" over a connection that already succeeded.
- The live chat owns the full window height. The stage is pinned to the layout's
  flexible row rather than counting siblings, because rows hidden in live mode used to
  push it onto a content-sized track and leave a dead slab under the composer.
- Provider failures are shown, never swallowed. Returning from an OAuth redirect that did
  not complete must say so in the panel; silence is indistinguishable from a no-op.

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

For security onboarding, use a compact three-rule disclosure before login: Auth0 identity,
24-hour provider credentials, and 60-day account data. After login, show the exact expiry
timestamps beside OpenRouter and Exa, and never imply that using the product extends them.
Name the standard-VPS limitation plainly without turning the primary task into legal prose.

## Acceptance

At 1440×900 and 390×844 there is no horizontal overflow, clipped action or overlapping
composer. Switching sessions replaces the transcript and the next model call receives that
session's prior turns. Good/Evil state is isolated. Missing comparison evidence is labeled
honestly. Feature commits update `CLAUDE.md`; UI-contract changes update this file.
Credential onboarding is not accepted until missing, connected, expired, scheduled-deletion
and immediate-deletion states pass keyboard and visual inspection.
