"""Simulated A07 DJ transition on fakes (no hardware).

Load+start A -> prepare B -> mix into B (crossfade) -> engage+adjust FX.
Run: PYTHONPATH=src python3 simulator.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from launchpad_mixxx import protocol as P
from launchpad_mixxx.app import DjApp
from launchpad_mixxx.clock import FakeClock
from launchpad_mixxx.endpoints import FakeLaunchpad, FakeMixxx
from launchpad_mixxx.mapping import PROFILES, ProfileId
from launchpad_mixxx.model import PadEvent


def pad(pid, cid, role="trigger"):
    for b in PROFILES[pid].bindings:
        if b.control_id == cid and b.role == role:
            return b.pad
    raise KeyError((pid, cid, role))


def tap(app, c, pid, cid, hold_ms=60, role="trigger"):
    p = pad(pid, cid, role)
    app.pad_event(PadEvent(p, False, True), c.now_ms())
    c.advance(hold_ms)
    app.tick(c.now_ms())
    app.pad_event(PadEvent(p, False, False), c.now_ms())
    c.advance(5)


def main():
    c = FakeClock(0)
    app = DjApp(launchpad=FakeLaunchpad(), mixxx=FakeMixxx(),
                initial_values={"deckA.gain": 80.0, "deckB.gain": 80.0,
                                "mixer.ch1": 100.0, "mixer.ch2": 0.0,
                                "mixer.crossfader": 0.0})
    D = ProfileId.DECKS
    # 1. Load + start track A
    tap(app, c, D, "deckA.load")
    tap(app, c, D, "deckA.play")
    tap(app, c, D, "deckA.sync")
    # 2. Prepare track B (load, cue, sync)
    tap(app, c, D, "deckB.load")
    tap(app, c, D, "deckB.cue")
    tap(app, c, D, "deckB.sync")
    tap(app, c, D, "deckB.play")
    # 3. Mix into B: crossfade hold 2 s (0 -> ~100 left-to-right side)
    p = pad(D, "mixer.crossfader", "inc")
    app.pad_event(PadEvent(p, False, True), c.now_ms())
    for _ in range(100):  # 100 x 20 ms = 2 s
        c.advance(20)
        app.tick(c.now_ms())
    app.pad_event(PadEvent(p, False, False), c.now_ms())
    # 4. Mixer/FX profile: enable FX on B + sweep mix knob 1 s
    app.pad_event(PadEvent(P.CC_USER1, True, True), c.now_ms())
    M = ProfileId.MIXER_FX
    tap(app, c, M, "fx.enableB")
    tap(app, c, M, "fx.enable1")
    p = pad(M, "fx.mix", "inc")
    app.pad_event(PadEvent(p, False, True), c.now_ms())
    for _ in range(50):
        c.advance(20)
        app.tick(c.now_ms())
    app.pad_event(PadEvent(p, False, False), c.now_ms())
    # 5. Back to decks, keep playing
    app.pad_event(PadEvent(P.CC_USER2, True, True), c.now_ms())

    cmds = app.mixxx.commands
    print(f"profile={app.router.active.value} mixxx_commands={len(cmds)}")
    print(f"crossfader={app.engine.get_value('mixer.crossfader'):.0f}% "
          f"fx.mix={app.engine.get_value('fx.mix'):.0f}%")
    seen = {(g, k) for g, k, _, _ in cmds}
    for want in [(("[Channel1]", "play")), (("[Channel2]", "play")),
                 (("[Master]", "crossfader")),
                 (("[EffectRack1_EffectUnit1]", "enable"))]:
        print(("OK  " if want in seen else "MISS"), want)
    assert ("[Channel1]", "play") in seen
    assert ("[Channel2]", "play") in seen
    assert ("[Master]", "crossfader") in seen
    print("A07-simulation PASS (fake endpoints; physical run Blocked — no MK2)")


if __name__ == "__main__":
    main()
