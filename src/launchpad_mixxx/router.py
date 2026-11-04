"""Profile router: pad events -> logical actions for the active profile.

- One active profile at a time; switching redraws LEDs, preserves Mixxx
  values, invalidates outstanding holds (P03/A06).
- Top-row CC_USER1/CC_USER2 always route to profile select (reserved).
- Grid notes route via the active profile's binding; unknown pads ignored.
- Delayed/stale releases (old generation) are dropped.
"""
from . import protocol as P
from .mapping import PROFILES, ProfileId
from .model import PadEvent


class ProfileRouter:
    def __init__(self, engine, profiles=PROFILES, initial=ProfileId.DECKS):
        self.engine = engine
        self.profiles = profiles
        self.active = initial
        # track which control+pad each press started, with generation, so a
        # delayed release after a profile switch cannot act on the new profile.
        self._press_registry: dict = {}  # pad -> (control_id|None, generation, profile)

    @property
    def profile(self):
        return self.profiles[self.active]

    def switch(self, pid: ProfileId):
        if pid == self.active:
            return False
        self.engine.invalidate_all()
        self._press_registry.clear()
        self.active = pid
        return True

    # -- entry points --------------------------------------------------
    def on_pad(self, ev: PadEvent, now_ms: int):
        if ev.is_top_row:
            return self._on_top_row(ev, now_ms)
        prof = self.profiles[self.active]
        binding = prof.by_pad(ev.pad)
        if ev.pressed:
            if binding is None:
                return []
            gen = self.engine.generation
            self._press_registry[ev.pad] = (binding.control_id, gen, self.active)
            if binding.ctype.value == "button":
                a = self.engine.press_button(binding.control_id, ev.pad)
            elif binding.role == "reset":
                a = self.engine.press_reset(binding.control_id, ev.pad)
            else:
                direction = +1 if binding.role == "inc" else -1
                a = self.engine.press_continuous(binding.control_id, direction,
                                                 ev.pad, now_ms)
                if a:
                    a.kind = binding.ctype.value
            if a:
                a.kind = binding.ctype.value if a.kind == "continuous" else a.kind
                return [a]
            return []
        else:
            reg = self._press_registry.pop(ev.pad, None)
            if reg is None:
                self.engine.release_pad(ev.pad)
                return []
            control_id, gen, prof_at_press = reg
            if prof_at_press != self.active or gen != self.engine.generation:
                return []  # stale: profile switched since press (A06)
            if control_id is None:
                return []
            self.engine.release(control_id, ev.pad, gen)
            return []

    def _on_top_row(self, ev: PadEvent, now_ms: int):
        if not ev.pressed:
            return []
        if ev.pad == P.CC_USER1:
            self.switch(ProfileId.MIXER_FX)
            return []
        if ev.pad == P.CC_USER2:
            self.switch(ProfileId.DECKS)
            return []
        return []
