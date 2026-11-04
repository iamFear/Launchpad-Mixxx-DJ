"""LED renderer: profile + press state -> colour/brightness (no Mixxx feedback).

R05: held pad bright; after release, dim in assigned colour.
D03: launch = DECKS; never-pressed = dim; unused = off; re-entry/reconnect =
     dim (fresh-press required); binary state does NOT change LEDs beyond
     press state (avoids feedback loops per PLAN).
"""
from .mapping import ProfileId
from .model import LedState


class LedRenderer:
    def __init__(self, profiles):
        self.profiles = profiles
        self.held: set = set()  # pads currently held

    def press(self, pad: int):
        self.held.add(pad)

    def release(self, pad: int):
        self.held.discard(pad)

    def clear_holds(self):
        self.held.clear()

    def render(self, active: ProfileId):
        out = []
        prof = self.profiles[active]
        for b in prof.bindings:
            bright = "bright" if b.pad in self.held else "dim"
            out.append(LedState(b.pad, False, b.color, bright))
        return out

    def full_redraw(self, active: ProfileId):
        self.clear_holds()
        return self.render(active)
