# Isolated BYOK retention

```yaml
item: isolated-byok-retention
branch: post-hackathon
phase: "—"
stage: S5-ship-learn
status: ready-to-ship
blocked_on: null
last: { agent: gpt-5, at: 2026-09-12T21:45:00-03:00, ledger: L-5 }
next_action: "Commit post-hackathon, push and verify Dokploy production health."
```

## Plan overview

Outcome: reduce credential exposure on a standard Hostinger VPS using a dedicated broker,
24-hour non-sliding credential retention, 60-day account-data retention and honest UX.
Non-goals: TEE, zero-knowledge claims, Auth0 identity deletion. Rollback: revert this change
and disable live BYOK; never restore server-wide user credentials.

Acceptance: broker alone owns keys/volume; AES-GCM fails closed; Auth0 scopes every access;
OpenRouter and Exa work through broker; 24-hour purge and 60-day purge are tested; onboarding
states are accessible and visually inspected; all repository gates pass.

## Decision log

DEC-1 | 2026-09-12 | S0-frame | owner
Context: standard public Hostinger VPS cannot provide confidential computing.
Decision: use a second maximally isolated container and retain provider keys for 24 hours.
Why: deliberately trades repeated onboarding friction for a smaller exposure window.

DEC-2 | 2026-09-12 | S1-plan | gpt-5
Context: storage-only isolation would return plaintext keys to the application.
Decision: broker also proxies provider traffic and validates Auth0 independently.
Why: keeps persisted secrets and routine plaintext provider use out of the main process.

## Ledger

### L-1 | 2026-09-12T17:45:00-03:00 | S0-frame | gpt-5 | framer | —
Did: framed threat model, retention split, UX disclosures and rollback.
Result: owner decision is testable and does not claim zero-knowledge.
Verified: owner message in current task.
Next: stage exit: outcome and security boundary accepted.

### L-2 | 2026-09-12T18:00:00-03:00 | S2-execute | gpt-5 | executor | —
Did: added credential broker, proxies, retention metadata, Exa BYOK UI and documentation.
Result: implementation ready for automated and visual verification.
Verified: none — verification follows after test completion.
Next: run repository gates and review the diff independently.

### L-3 | 2026-09-12T21:20:00-03:00 | S3-review | security-review | reviewer | —
Did: independently reviewed Auth0, broker proxy scope, retention and deletion races.
Result: found fail-open production auth, broad proxy access, retained bearer/world state and
an unauthenticated-session UI race. Also recorded the honest limitation that 60-day data is
not user-key zero-knowledge on a standard VPS.
Verified: read-only diff review plus automated gates.
Next: remediate every release-blocking finding before commit.

### L-4 | 2026-09-12T21:40:00-03:00 | S4-remediate | gpt-5 | remediator | L-3
Did: made production auth fail closed, removed global world credentials from Compose,
allowlisted broker operations and payload size, made provider bearers mission-scoped, canceled
tasks and evicted worlds/event buses before deletion, moved 60-day purge into the live process,
and fixed onboarding contrast, transient 401 and replay connection language.
Result: blockers remediated; final gates and deployment verification remain.
Verified: compile, backend suites, web tests/build, Compose parse, visual light/dark/replay/compare.
Next: final gate, commit and deploy exclusively from post-hackathon.

### L-5 | 2026-09-12T21:45:00-03:00 | S5-ship-learn | gpt-5 | shipper | L-4
Did: ran compile, broker/server/session/offline suites, frontend tests/build, Compose parse,
secret-pattern scan, whitespace gate and visual audits of onboarding, themes, Replay and Compare.
Result: source is ready to ship from post-hackathon; Docker image build remains delegated to
Dokploy because the local Docker daemon is unavailable.
Verified: all executable local gates green; VPS operational preflight green.
Next: commit, push, then verify the deployed exact commit and public health.
