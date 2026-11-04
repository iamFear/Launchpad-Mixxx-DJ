# Implementation tasks

All implementation tasks start pending. The existing Notion knob task corresponds to T04. Mark tasks complete only when the specified evidence exists.

| Task | Depends on | Work | Evidence required |
| --- | --- | --- | --- |
| T01 | — | Inspect the branch and run the Launchpad/Mixxx integration spike. Resolve D05. | MIDI input and LED observations on the MK2, plus successful live transport and continuous-control commands. |
| T02 | T01 | Resolve D01–D04 and produce a pad map for both profiles. Reserve the two selectors and validate pad capacity. | Decision record and complete pad map with explicit deck ownership and action/color assignments. |
| T03 | T01 | Build hardware and Mixxx endpoints, profile routing, and press-state LED rendering. Final LED behavior depends on T02. | A01, A02, A03, and A06, with fake-endpoint coverage for stale events and duplicate actions. |
| T04 | T01, D04 | Implement the knob engine with a clock-driven repeat, clamping, and hold cancellation. A fake-clock prototype can proceed while D04 is open. | A04 and relevant A06 cases. |
| T05 | T02–T04 | Wire both decks to User 2 and mixer/effects to User 1. Implement the resolved fader and button behavior. | A02, A03, and A05 on the actual layout. |
| T06 | T05 | Package the app, write the setup and operation steps, and verify a clean installation and the DJ workflow. | All applicable cases pass, including physical A07. Record versions, commit, and observed results. |
