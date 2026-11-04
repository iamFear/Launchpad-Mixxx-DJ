"""Shared value objects. Raw MIDI never leaks past the launchpad boundary."""
from dataclasses import dataclass
from typing import Literal

Color = Literal["red", "green", "yellow", "off"]
Brightness = Literal["dim", "bright", "off"]


@dataclass(frozen=True)
class PadEvent:
    pad: int  # grid MIDI note (Session layout) or CC number for top row
    is_top_row: bool
    pressed: bool  # True = press (vel 127 / note-on 127), False = release
    channel: int = 0


@dataclass(frozen=True)
class LedState:
    pad: int
    is_top_row: bool
    color: Color
    brightness: Brightness

    def palette_velocity(self) -> int:
        from . import protocol as P

        if self.color == "off" or self.brightness == "off":
            return P.LED_OFF
        return P.PALETTE[(self.color, self.brightness)]


@dataclass
class LogicalAction:
    """What the router/engine decided: a Mixxx-bound action, no MIDI in it."""
    control_id: str       # e.g. "deckA.play", "mixer.crossfader"
    kind: str             # "button" | "knob" | "fader"
    direction: int = 0    # knob/fader: +1 inc, -1 dec, 0 = reset/set
    value01: float | None = None  # normalized 0..1 snapshot for continuous
    generation: int = 0   # invalidates stale repeats after profile switch
