# Setup & operation (macOS + Mixxx 2.5.x + Launchpad MK2)

## Install
1. `python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt` — add `mido python-rtmidi` for live
   MIDI (tests/simulator run without them on fakes).
3. Mixxx 2.5.x: Preferences → Controllers → check for the bridge port,
   or Learning Wizard; or copy `mixxx_mapping/LaunchpadMK2Bridge.midi.xml`
   into the Mixxx user controller-mapping folder, then enable it.

## Launch / shutdown order
1. Start Mixxx, enable the `LaunchpadMK2Bridge` mapping.
2. Plug in the MK2 (Session layout; User1/User2 bootloader channels default).
3. Start the app (`PYTHONPATH=src python3 main.py` — live mode needs
   hardware + `mido`; without them it reports what is missing).
4. Press **User 2** (decks) or **User 1** (mixer/FX); play. Shutdown: quit
   app first, then unplug, then quit Mixxx.

## Operation
- Green pad = hold to increase, red = hold to decrease (1% per 20 ms).
- Yellow pad = one action per press (hold does nothing extra).
- Knob yellow pad = reset to centre (50%). Switching profiles or
  unplugging cancels all holds — press again after re-entry.

## Troubleshooting
- *App sees no MK2:* check Audio MIDI Setup lists it; try another USB port;
  confirm Session layout (all LEDs off = app not running / wrong port).
- *Mixxx gets nothing:* verify the bridge virtual port is enabled in
  Preferences → Controllers and the XML mapping is assigned to it.
- *LED colours look wrong:* recalibrate `src/launchpad_mixxx/protocol.py`
  `PALETTE` against the MK2 colour table (D03 open point).
- *Value jumps on first touch:* by design the app owns 0–100% state and
  Mixxx follows; move the control to reconcile (no soft-takeover in v1).
