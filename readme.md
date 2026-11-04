# Launchpad-Mixxx-DJ

**Play a full DJ set in Mixxx with a single Novation Launchpad MK2 — two CDJ-style decks, mixer, and FX, no DJ controller needed. Built for the Meta hackathon.**

Mixxx stays in charge of audio. The app (or its on-screen emulator) turns pad presses into Mixxx commands over MIDI and drives the Launchpad LEDs: green = increase, red = decrease, yellow = one action per press.

## Demo (no hardware needed)

```bash
pip install -r requirements.txt
python3 -m pytest tests/ -q                 # 16 passed
PYTHONPATH=src python3 main.py --emulator   # on-screen Launchpad → live Mixxx
PYTHONPATH=src python3 simulator.py         # scripted two-track transition
```

Or double-click **`dist/Launchpad-Mixxx-DJ.app`** (build it with
`bash macos/build_app.sh`) — same emulator, no Terminal needed.

Click LOAD → PLAY on Deck A, prep Deck B, hold crossfader ▲ ~2 s, flip to User 1 for mixer/FX. The emulator panel logs every command Mixxx receives.

## How it works

```text
Launchpad MK2 ──MIDI──▶ app: launchpad endpoint → profile router → control engine ──CoreMIDI──▶ Mixxx
                    (raw MIDI)      (User1/User2)      (20 ms repeats)      (virtual port + XML mapping)
```

- **Two profiles.** Physical **User 2** = decks (Deck A left half, Deck B right half). Physical **User 1** = mixer + FX. Selectors stay reserved; switching redraws LEDs, preserves Mixxx values, kills stale holds.
- **Knobs** (3 pads: red ▼ / yellow reset / green ▲) and **faders** (2 pads: red ▼ / green ▲) move 1% per 20 ms hold, clamped 0–100%. **Buttons** (1 yellow pad) fire exactly once per press.
- **LEDs follow press state** (bright held, dim released) — never Mixxx state, so feedback can't loop back as input.

## Pad maps

**Decks (User 2)** — per deck: LOAD / PLAY / CUE / SYNC + GAIN / RATE / FILTER knobs + PFL; shared crossfader + headphone controls on the bottom row.

| Row | Col 0–3 (Deck A) | Col 4–7 (Deck B) |
| --- | --- | --- |
| 0 | LOAD · PLAY · CUE · SYNC | LOAD · PLAY · CUE · SYNC |
| 1 | GAIN knob (▼ ═ ▲) | GAIN knob (▼ ═ ▲) |
| 2 | RATE knob (▼ ═ ▲) | RATE knob (▼ ═ ▲) |
| 3 | FILTER knob (▼ ═ ▲) | FILTER knob (▼ ═ ▲) |
| 4 | PFL (c1) | PFL (c5) |
| 7 | HEADMIX · · XFADE ▼▲ · HEADPHONES | (shared, centre) |

**Mixer + FX (User 1)**

| Row | Pads |
| --- | --- |
| 0 | CH1 fader ▼▲ · CH2 fader ▼▲ · XFADE ▼▲ |
| 1 | MUTE 1 · MUTE 2 · PFL 1 · PFL 2 |
| 2 | MASTER knob · HEADMIX knob |
| 4 | FX MIX knob · FX PARAM knob |
| 6 | FX ON · FX→A · FX→B |

## Setup with Mixxx 2.5.x

1. `pip install -r requirements.txt` (macOS: stdlib + tkinter only; `pyobjc` for window focus).
2. Copy `mixxx_mapping/LaunchpadMK2Bridge.midi.xml` into Mixxx's user controllers folder, e.g.
   `~/Library/Containers/org.mixxx.mixxx/Data/Library/Application Support/Mixxx/controllers/`.
3. Mixxx → Preferences → Controllers → enable `LaunchpadMK2Bridge` with the `Launchpad MK2 DJ Bridge` mapping.
4. Run the emulator, or connect the MK2 and run `PYTHONPATH=src python3 main.py`.

Details, per-part walkthroughs, and troubleshooting: [`docs/EMULATOR.md`](docs/EMULATOR.md), [`docs/SETUP.md`](docs/SETUP.md), and the full [`docs/Launchpad-Mixxx-DJ-Manual.pdf`](docs/Launchpad-Mixxx-DJ-Manual.pdf).

## Project layout

```text
src/launchpad_mixxx/  protocol · clock · mapping · engine · router ·
                      leds · endpoints · coremidi_bridge · app · emulator
mixxx_mapping/        LaunchpadMK2Bridge.midi.xml (generated from code)
tests/                engine repeats · routing/LEDs · emulator · acceptance
docs/                 DECISIONS · SETUP · EMULATOR · VERIFICATION · PDF manual
agents/               SPEC · PLAN · TASKS · ACCEPTANCE (build contract)
```

## Verification status

16/16 deterministic tests pass (fake clock/endpoints), including the literal acceptance timing: 1% @ 20 ms, 50% @ 1 s, 100% @ 2 s. Results per case in [`docs/VERIFICATION.md`](docs/VERIFICATION.md). All **physical** acceptance portions (real MK2 + live Mixxx timing) are recorded as Blocked pending hardware — the logic suite is green and simulation-ready.

## Decisions & scope

Resolutions for D01–D05 (fader colours, exact pad map, LED states, knob edges, integration route) with evidence: [`docs/DECISIONS.md`](docs/DECISIONS.md). First delivery targets macOS + Mixxx 2.5.x + Launchpad MK2; other platforms, controllers, and Mixxx-side LED feedback are out of scope.

MIT — see `LICENSE`.
