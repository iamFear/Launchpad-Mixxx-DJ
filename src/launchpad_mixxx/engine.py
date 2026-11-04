"""Control engine: held-input repeats, clamping, hold cancellation.

Contract (SPEC P01/P02, decisions D01/D04):
- Knob/fader values are 0..100%. The first step fires on the first 20 ms
  tick (no immediate step on press), then +1 (or -1) per 20 ms while held.
- 0% + hold inc => 1% at 20 ms, 50% at 1 s, 100% at 2 s (A04 literal).
  A tap shorter than 20 ms yields no change (below scheduler resolution;
  intentional taps are virtually never that short). Clamp at bounds.
- Symmetric decrease. Both pads of one control held -> last-press wins.
- Yellow button: exactly one action per press; hold stays bright, no repeat.
- Release cancels pending repeats. Profile switch / device loss cancels all
  holds of the old generation; delayed releases cannot leak into the new
  profile (A06). Fresh press required after switch/reconnect.
"""
from dataclasses import dataclass, field

TICK_MS = 20
STEP_PCT = 1.0
MIN_PCT, MAX_PCT = 0.0, 100.0


@dataclass
class _Hold:
    control_id: str
    direction: int  # +1 | -1
    value: float
    next_tick: int
    generation: int
    pad: int


@dataclass
class EngineResult:
    actions: list = field(default_factory=list)  # LogicalAction
    state: dict = field(default_factory=dict)    # control_id -> value


class ControlEngine:
    def __init__(self, initial: dict | None = None):
        self.values: dict = dict(initial or {})
        self.holds: dict = {}  # control_id -> _Hold
        self.generation = 0
        self.armed_buttons: set = set()  # (generation, pad) pressed-not-released

    # -- lifecycle -----------------------------------------------------
    def set_value(self, control_id: str, value: float):
        self.values[control_id] = max(MIN_PCT, min(MAX_PCT, float(value)))

    def get_value(self, control_id: str, default: float = 50.0) -> float:
        return self.values.get(control_id, default)

    def invalidate_all(self):
        """Profile exit / device loss: drop holds, require fresh presses."""
        self.generation += 1
        self.holds.clear()
        self.armed_buttons.clear()

    # -- input ---------------------------------------------------------
    def press_continuous(self, control_id: str, direction: int, pad: int,
                         now_ms: int, initial_value: float | None = None):
        """inc/dec pad of a knob or fader. Last-press wins (D04).

        No immediate step: the first step fires on the first 20 ms tick, so
        the A04 contract (1% at 20 ms, 50% at 1 s, 100% at 2 s) holds
        literally. Returns None (the tick emits the actions).
        """
        assert direction in (+1, -1)
        base = self.get_value(control_id) if initial_value is None else initial_value
        base = max(MIN_PCT, min(MAX_PCT, float(base)))
        self.values[control_id] = base
        self.holds[control_id] = _Hold(control_id, direction, base,
                                       now_ms + TICK_MS, self.generation, pad)
        return None

    def press_reset(self, control_id: str, pad: int, default: float = 50.0):
        """Yellow pad of a knob: single reset, cancels any hold (D04)."""
        self.values[control_id] = default
        self.holds.pop(control_id, None)
        from .model import LogicalAction
        return LogicalAction(control_id, "reset", 0, default / 100.0, self.generation)

    def press_button(self, control_id: str, pad: int):
        """Yellow standalone button: exactly one action per press (P02)."""
        key = (self.generation, pad)
        if key in self.armed_buttons:
            return None  # held repeat suppressed
        self.armed_buttons.add(key)
        from .model import LogicalAction
        return LogicalAction(control_id, "button", 0, None, self.generation)

    def release(self, control_id: str | None, pad: int, generation: int | None = None):
        """Release cancels repeats/rearms. Stale generations are ignored (A06)."""
        if generation is not None and generation != self.generation:
            return False
        if control_id and control_id in self.holds and self.holds[control_id].pad == pad:
            del self.holds[control_id]
        self.armed_buttons.discard((self.generation, pad))
        # also drop any hold tracked under a different pad of same control if
        # this release belongs to the winning hold (last-wins: one hold/ctrl).
        return True

    def release_pad(self, pad: int):
        for cid, h in list(self.holds.items()):
            if h.pad == pad:
                del self.holds[cid]
        self.armed_buttons = {k for k in self.armed_buttons if k[1] != pad}

    # -- time ----------------------------------------------------------
    def tick(self, now_ms: int):
        from .model import LogicalAction
        out = []
        for cid, h in list(self.holds.items()):
            if h.generation != self.generation:
                del self.holds[cid]
                continue
            while h.next_tick <= now_ms:
                nxt = h.value + h.direction * STEP_PCT
                if nxt < MIN_PCT:
                    nxt = MIN_PCT
                elif nxt > MAX_PCT:
                    nxt = MAX_PCT
                h.value = nxt
                h.next_tick += TICK_MS
                self.values[cid] = nxt
                out.append(LogicalAction(cid, "continuous", h.direction,
                                         nxt / 100.0, h.generation))
                if nxt in (MIN_PCT, MAX_PCT):
                    # stay held at bound: keep hold alive but emit no more
                    # until time passes? Spec A04: "keep holding and value
                    # stays at 100%". We keep emitting clamped values would
                    # spam Mixxx; instead hold position without duplicates.
                    h.next_tick = now_ms + TICK_MS
                    break
        return out
