# Verification record

Run: `python3 -m pytest tests/ -q` → **16 passed** (commit `dev` HEAD at
build time). Simulator: `PYTHONPATH=src python3 simulator.py` → PASS.
Fake-endpoint evidence is deterministic; every physical portion is
**Blocked** (no MK2 / live Mixxx in this environment).

| Case | Covers | Fake result | Physical | Notes |
| --- | --- | --- | --- | --- |
| A01 | R01 | Pass (`test_top_row_selectors…`, app boots from clean checkout, pad→LED→1 Mixxx cmd) | Blocked | Clean-install + live ports pending T06 |
| A02 | R02 R03 R08 | Pass (`test_profile_switch…`, `test_inactive_profile…`) | Blocked | Profile isolation proven on fakes |
| A03 | R04–R06 | Pass (`validate()`, bright-held/dim-released, D03 states) | Blocked | Palette numbers provisional |
| A04 | R07 P01 | Pass (literal: 1% @20 ms, 50% @1 s, 100% @2 s, clamp, release-cancel, symmetric dec, last-wins, tap<20 ms noop) | Blocked | HW run must record scheduling jitter |
| A05 | R04 R06 P02 | Pass (D01 green-inc/red-dec; exactly one action/press; rearm) | Blocked | — |
| A06 | R02 R03 P01 P03 | Pass (switch/unplug emits nothing, stale release dropped, LEDs rebuilt dim, fresh press works) | Blocked | — |
| A07 | R01–R03 R08 | Pass on fakes (`simulator.py`: load A → play → prep B → 2 s crossfade → FX enable+sweep → back to decks, 159 cmds) | Blocked | Full DJ transition needs MK2 + Mixxx |

Release: **not granted** — all physical portions Blocked per ACCEPTANCE.md
("report an unavailable device as Blocked"). The fake-clock/logic suite is
green and the app is demoable in simulation.
