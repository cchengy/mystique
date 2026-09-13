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
  24 hours in an encrypted, isolated broker, and that sessions and memory follow the
  60-day rule. Never soften this into generic “secure” copy. The product never *claims*
  zero-knowledge: that statement is made in plain language in the privacy notice, which is
  one click from the gate and always reachable, rather than as hosting detail on the way
  in — an onboarding card is not the place to describe the server's threat model.
- The gate is the screen's subject, not a panel in a column: the app dims behind it, the
  card is centred, holds one proportion and never scrolls at ordinary heights. It carries
  only what getting in requires — provider extras and the data lifecycle live in the rail,
  with deletion still one click away. When the account unlocks, a slanted comic panel
  gutter wipes the card while it shifts colour toward her red, and the dimmed app comes
  back to full strength; `prefers-reduced-motion` cuts straight to the app.
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
- Two languages, one source. Every visible string is written in English in the component
  and translated through `pt.ts`, keyed by that exact source string; an untranslated string
  falls back to English instead of breaking. The choice is the user's, sits next to the
  theme toggle, persists, and defaults to the browser's language. She answers in the
  language the app is being read in.
- The privacy notice is dismissible but never unreachable: accepting it is remembered, and
  a Privacy link in the rail brings it back at any time, on desktop and on mobile.
- Compare is the product's argument, so it is built as one: the question, then two ledgers
  that answer it with the same three figures, the same run cards and the same bank. The
  rows line up across the two sides (subgrid) — a comparison whose rows drift is not
  comparing anything. A run card is a button back into that conversation. The only
  differences between the sides are the accent and what each one left behind.
- The account panel has one type ramp per context — `--p-title/-text/-small/-label`, bound
  once for the gate and one step down for the rail. No display face inside a 15rem sidebar,
  and no size that is not on the ramp.
- Panel controls share one surface, one height with their inputs, and visible hover, active
  and disabled states in both themes. Identity sits above its Sign out button, never beside
  it: at rail width the email loses to the button every time.
- What she has learned is readable by the person who owns it: the engine's own `WIKI.md`,
  per profile, at the foot of each ledger.
- The gate is modal in behaviour, not just in appearance: the way in takes focus when it
  opens, Tab cycles inside it, and focus returns to where it came from when it lets go.
  There is no Escape — the gate is the only way in, so there is nothing to escape to.
- A new account starts empty. Nothing in the browser — least of all the pre-accounts
  transcript — may become an account's first conversation.
- The guided tour uses the gate's scene grammar and adds travel: two short panels introduce
  her in the middle of the screen, then the card leaves the middle and settles under each
  control it is describing — Good, Evil, Guided replay, Live chat, Compare endings, and the
  composer, in that order — with the control itself raised through the veil and still
  usable — the highlight is the control's own outline, never a second box drawn near it,
  so it cannot drift out of register with what it is pointing at. The card moves by
  transform only, and it does not glide between controls — it is taken apart and put back
  together at the other end:

  | Beat | Duration | Easing | What moves |
  |---|---|---|---|
  | Anticipation + funnel out | 170ms | `cubic-bezier(.55,0,1,.45)` | the card leans back, then is drawn into a sliver toward its destination — `transform-origin` sits on the side it is heading for, which is what makes it a funnel and not a shrink |
  | Streak | 420ms | `cubic-bezier(.2,.8,.2,1)` | a line in `--secundaria` crosses the gap it just jumped, wiped in and then out |
  | Unfold + settle | 300ms | `cubic-bezier(.16,1,.3,1)` | it opens from the sliver with one counter-squash, colour draining back to rest |

  Peaks sit early in each beat, so it reads as a flash rather than a slow stretch, and there
  is no overshoot. `--secundaria` is the violet the gate shifts through on its way out; it
  belongs to motion and never to a resting surface. The positioned element carries only its
  place on screen — the shape, the frame, the shadow and the pointer all live on one inner
  layer, because a funnel that leaves its own border standing still reads as the contents
  draining out of a box. Its copy is the product's own words; the tour
  explains what is there and never invents a second story about it. The last card reads the
  account: connect a key, or connect Exa for sourced search, or just send a mission.
- Seeing the tour is remembered on the account, not in the browser: it does not reappear on
  a second device, it is not lost by clearing storage, and every account that has never
  seen it — including accounts created before it existed — gets it once. The button beside
  the theme toggle replays it at any time.
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
