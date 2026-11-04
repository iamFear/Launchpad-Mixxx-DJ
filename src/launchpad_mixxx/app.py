"""Application orchestrator: wires endpoints + router + engine + LEDs.

LED output is never routed back as input (PLAN). Mixxx values are preserved
across profile switches (no commands emitted on switch/reconnect — A06).
"""
from . import protocol as P
from .endpoints import FakeLaunchpad, FakeMixxx
from .engine import ControlEngine
from .leds import LedRenderer
from .mapping import PROFILES, ProfileId
from .model import PadEvent
from .router import ProfileRouter


class DjApp:
    def __init__(self, launchpad=None, mixxx=None, profiles=PROFILES,
                 initial=ProfileId.DECKS, initial_values=None):
        self.engine = ControlEngine(initial_values)
        self.router = ProfileRouter(self.engine, profiles, initial)
        self.leds = LedRenderer(profiles)
        self.launchpad = launchpad or FakeLaunchpad()
        self.mixxx = mixxx or FakeMixxx()
        self.redraw()

    # -- inputs ------------------------------------------------------
    def pad_event(self, ev: PadEvent, now_ms: int):
        if ev.pressed and not ev.is_top_row:
            self.leds.press(ev.pad)
        elif not ev.pressed and not ev.is_top_row:
            self.leds.release(ev.pad)
        before = self.router.active
        actions = self.router.on_pad(ev, now_ms)
        if self.router.active != before:
            self.leds.clear_holds()
            self.redraw()
        else:
            self._push_leds_for_pad(ev.pad)
        for a in actions:
            self.mixxx.send(a)
        # pump due repeats immediately (tick is also called by the run loop)
        for a in self.engine.tick(now_ms):
            self.mixxx.send(a)
        return actions

    def tick(self, now_ms: int):
        for a in self.engine.tick(now_ms):
            self.mixxx.send(a)

    def switch_profile(self, pid: ProfileId):
        if self.router.switch(pid):
            self.leds.clear_holds()
            self.redraw()

    def device_lost(self):
        self.engine.invalidate_all()
        self.leds.clear_holds()

    def device_reconnected(self):
        # Rebuild LEDs, require fresh presses, send nothing (A06).
        self.redraw()

    # -- leds --------------------------------------------------------
    def _push_leds_for_pad(self, pad: int):
        prof = self.router.profile
        b = prof.by_pad(pad)
        if b is None:
            return
        bright = "bright" if pad in self.leds.held else "dim"
        from .model import LedState
        self.launchpad.set_led(LedState(pad, False, b.color, bright))

    def redraw(self):
        for led in self.leds.full_redraw(self.router.active):
            self.launchpad.set_led(led)
        # profile selector indication on top row
        from .model import LedState
        self.launchpad.set_led(LedState(
            P.CC_USER1, True, "yellow",
            "bright" if self.router.active == ProfileId.MIXER_FX else "dim"))
        self.launchpad.set_led(LedState(
            P.CC_USER2, True, "yellow",
            "bright" if self.router.active == ProfileId.DECKS else "dim"))


def build_default_app(**kw) -> DjApp:
    return DjApp(**kw)
