# META's Hackaton: Launchpad Maping Project with Mixxx

macOS bridge app: play a full Mixxx 2.5.x set on a single Novation
Launchpad MK2 as two CDJ-style decks + mixer + FX.

- **User 2** → decks profile (Deck A left, Deck B right): Load / Play /
  Cue / Sync + Gain / Rate / Filter knobs + PFL, shared crossfader.
- **User 1** → mixer/FX profile: Ch1/Ch2 volume + crossfader faders,
  Mute/PFL, Master/HeadMix knobs, FX mix/param knobs + enables.
- Green = increase, red = decrease (1% per 20 ms hold), yellow = one action
  per press. Held pads glow bright, released pads dim.

## Quick start (no hardware needed for tests/sim)

```bash
pip install -r requirements.txt
python3 -m pytest tests/ -q          # 16 passed
PYTHONPATH=src python3 simulator.py  # scripted A07 DJ transition on fakes
```

No Launchpad? Run the on-screen emulator — it drives Mixxx while Mixxx is
open, no hardware needed (see `docs/EMULATOR.md`):

```bash
PYTHONPATH=src python3 main.py --emulator
```

Live use needs the MK2 + `mido`/`python-rtmidi`: see `docs/SETUP.md`,
decisions in `docs/DECISIONS.md`, results in `docs/VERIFICATION.md`,
Mixxx mapping in `mixxx_mapping/LaunchpadMK2Bridge.midi.xml`.

Spec/plan/tasks/acceptance live in `agents/` and are implemented per
`agents/AGENTS.md` (T01–T05 logic complete on fakes; physical A01–A07
portions Blocked pending hardware).
