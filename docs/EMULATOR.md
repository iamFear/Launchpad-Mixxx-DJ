# Emulator → Mixxx (no hardware needed)

The app ships an on-screen Launchpad MK2 emulator that drives Mixxx
**while Mixxx is open**, over a CoreMIDI virtual port. Verified on:
macOS 27.0.1 arm64, Python 3.13.9, Mixxx 2.5.6, no physical Launchpad.

## 1. Install the bridge mapping into Mixxx (one time)

In YOUR Terminal (the app sandbox cannot write into Mixxx's folder):

```bash
MAP=~/Library/Containers/org.mixxx.mixxx/Data/Library/Application\ Support/Mixxx/controllers
mkdir -p "$MAP"
cp mixxx_mapping/LaunchpadMK2Bridge.midi.xml "$MAP/"
```

Then in Mixxx: **Preferences → Controllers** → select the
`LaunchpadMK2Bridge` device → enable it with the
`Launchpad MK2 DJ Bridge` mapping → OK. (If the device only appears while
the emulator runs, start step 2 first, then open Preferences.)

## 2. Launch the emulator

```bash
PYTHONPATH=src python3 main.py --emulator
```
(or double-click `dist/Launchpad-Mixxx-DJ.app` after `bash macos/build_app.sh`)

You get an 8×8 pad grid plus Session / User 1 / User 2 / Mixer buttons.
Click-and-hold pads exactly like hardware:

- **Green** = hold to increase, **red** = hold to decrease (1% per 20 ms).
- **Yellow** = one action per click (play, cue, sync, load, mutes, FX…).
- Yellow pad inside a knob triple = reset that control to centre (50%).
- **User 2** = decks (Deck A left, Deck B right); **User 1** = mixer + FX.
- The right-hand panel logs every command sent to Mixxx
  (`[Channel1] play 1.00`, …). The header confirms
  `MIDI live → Mixxx on 'LaunchpadMK2Bridge'`.

## 3. Self-check (optional but recommended)

The bundle can verify itself — window, 64 pads, live MIDI port, a synthetic
press, hold-repeats, and a profile switch — and writes the report to
`/tmp/launchpad_selftest.json`:

```bash
open dist/Launchpad-Mixxx-DJ.app --args --selftest
```

Expect `"ok": true` (plus `window_viewable`, `midi_live`,
`press_one_command`, `hold_ok`, `switch_ok` all true).

## 4. Play the A07 set

Load + start track A (User 2 → LOAD, PLAY), prepare B (LOAD, CUE, SYNC,
PLAY), hold the crossfader ▲ pad ~2 s to mix over, press User 1 for
mixer/FX, click an FX enable + hold FX MIX ▲, then back to User 2.

## Troubleshooting

- *Emulator says "MIDI unavailable":* you are not on macOS or CoreMIDI
  denied access — commands are still recorded in the log panel.
- *Mixxx doesn't react:* mapping not installed/enabled (step 1), or the
  emulator was started after opening Preferences (re-open Preferences).
- *Two `LaunchpadMK2Bridge` ports in Mixxx:* an old emulator instance is
  still running — quit it (`pkill -f 'main.py --emulator'`).
- *Mixxx's own LEDs:* v1 only sends app→Mixxx; Mixxx-side LED feedback is
  out of scope (D03: LEDs follow press state, not Mixxx state).
