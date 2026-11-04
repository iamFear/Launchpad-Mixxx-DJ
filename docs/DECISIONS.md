# Decision record (resolves SPEC D01–D05)

Environment at build: macOS 27.0.1 arm64, Python 3.13.9, pytest 8.4.2,
Mixxx target 2.5.x (mapping `schemaVersion="1"`, `mixxxVersion="2.5.0"`).
No physical Launchpad MK2 was available — all hardware observations below
are taken from documentation (Blocked for physical re-verification in T06).

## T01 / D05 — integration route and versions
- **Chosen:** macOS MIDI bridge app (Python, CoreMIDI via `mido` +
  `python-rtmidi`) + declarative Mixxx XML mapping
  (`mixxx_mapping/LaunchpadMK2Bridge.midi.xml`). The app owns LEDs and all
  repeat/profile logic; Mixxx owns audio. Reconciliation policy: bounded —
  the app keeps its own 0–100% values, translates to 0..127 bridge MIDI,
  and never overwrites its values from Mixxx (avoids parameter jumps; the
  XML uses `<normal/>`, no soft-takeover — documented limitation).
- **Alternative rejected:** Mixxx JS controller script — would duplicate
  repeat/profile state inside Mixxx and is untestable without hardware.
- **References:** Novation *Launchpad MK2 Programmers Reference Manual
  v1.03* — grid = Note On (vel 127 press / vel 0 release), velocity sets LED
  colour; top row = CC 104–111 (127/0); layouts via SysEx
  `F0 00 20 29 02 18 22 <00 Session|01 User1|02 User2> F7`; Session layout
  notes = row×10+col (bottom-left 11 … top-right 88); Session = ch 1, User 1
  = ch 6–8, User 2 = ch 14–16 (bootloader); ch 2 = flash, ch 3 = pulse.
  Mixxx mapping format: Mixxx wiki *MIDI Controller Mapping File Format*
  + *MIDI Scripting* (XML `<control>` group/key/status/midino, 2.5.x two-file
  XML+JS system). App stays in **Session layout / ch 1** for the grid and
  uses top-row CC 109 (User 1) / 110 (User 2) as profile selectors —
  assumed CC order Up 104 … Mixer 111, **to verify physically (Blocked)**.
- **Setup:** `pip install -r requirements.txt` (`mido python-rtmidi`
  optional — fakes work without them); copy the XML into Mixxx
  Preferences → Controllers; launch order: Mixxx → app → plug MK2
  (details in SETUP.md).

## D01 — fader colour/direction/step (RESOLVED)
Fader = 2 pads: **GREEN = increase, RED = decrease** (extends the R04 legend;
overrides the R06 draft "yellow and red"). Same engine as knobs: first step
on first 20 ms tick, 1 pp per 20 ms, clamp 0/100%. Rationale: one legend for
all continuous controls; yellow stays exclusively binary.

## D02 — exact controls and pad ownership (RESOLVED)
`src/launchpad_mixxx/mapping.py` is the contract; `validate()` enforces
unique pads, required pad counts (button 1 / knob 3 / fader 2), and colour
sets. User 2 = decks (left half Deck A `[Channel1]`, right half Deck B
`[Channel2]`): per deck Load / Play / Cue / Sync buttons + Gain / Rate /
Filter knobs + PFL button; shared crossfader fader + headmix/headcue buttons.
User 1 = mixer/FX: Ch1/Ch2 volume faders, crossfader fader, Mute/PFL buttons,
Master + HeadMix knobs, FX mix/param knobs, FX enable + per-deck route
buttons. 34 (decks) + 21 (mixer/FX) pads — fits 64, selectors reserved.
Covers the A07 two-track transition; headphone EQ/sync included, hotcues
explicitly out of first-delivery scope.

## D03 — launch/profile/LED states (RESOLVED)
Launch profile = **DECKS**. Never-pressed = dim in assigned colour; unused
pads = off; re-entered/reconnected pads = dim (fresh press required);
binary Mixxx state does **not** alter LEDs (press-state only) to avoid
feedback loops. Selector CCs light bright on the active profile.

## D04 — knob edge behaviour (RESOLVED)
Symmetric ±1 pp per 20 ms tick, first step on first tick (A04 literal: 1% @
20 ms, 50% @ 1 s, 100% @ 2 s from 0%). Tap <20 ms = no change (below
scheduler resolution; intentional taps are ≥50 ms). Both pads held =
**last-press wins**; any release cancels that knob/fader (fresh press needed).

## Palette calibration (OPEN, blocked on hardware)
`protocol.PALETTE` provisional: red 1/5, green 17/21, yellow 9/13
(dim/bright), off 0. Calibrate dim/bright entries against a physical MK2
during T01/T06; single-spot change.
