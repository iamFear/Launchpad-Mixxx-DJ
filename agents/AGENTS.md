# Launchpad-Mixxx-DJ agent guide

Place this file at the repository root alongside the other four Markdown files. Read them in this order.

| File | Purpose |
| --- | --- |
| [SPEC.md](SPEC.md) | Product requirements, provisional behavior, and open decisions |
| [PLAN.md](PLAN.md) | Proposed architecture and integration experiments |
| [TASKS.md](TASKS.md) | Ordered, independently verifiable work |
| [ACCEPTANCE.md](ACCEPTANCE.md) | Requirement traceability and release checks |

## Workflow

1. Inspect the active branch and check for newer project instructions. The planning baseline was `main` at `c11808d` (MIT license) and `dev` at `65f89a6` (license and a one-heading `readme.md`).
2. Start at T01. Use the experiments in the plan to settle technical decisions. Record the exact software versions, observed behavior, and links to evidence in the affected task or decision.
3. Resolve product decisions in the spec before implementing the affected behavior. Continue independent work while a decision is open.
4. Implement one task at a time. For behavior changes, update the spec and acceptance cases first, then implementation and verification.
5. Report each applicable case as Pass, Fail, or Blocked. Keep simulated evidence separate from physical Launchpad and live Mixxx evidence. Record the commit and environment for each run.

Keep Mixxx in charge of audio playback and mixing. Keep raw MIDI details at the hardware boundary and Mixxx control identifiers at the integration boundary. Use an injectable clock and fake endpoints for timing and routing tests. Preserve the MIT license.
