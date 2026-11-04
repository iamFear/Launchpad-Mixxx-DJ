"""Mapping contract: one entry per pad, unique addresses per profile.

Decisions encoded (see docs/DECISIONS.md):
- D01: fader = 2 pads GREEN(+)/RED(-), 1% per 20 ms hold, 0..100% clamp.
- D02: pad map below; left half = Deck A, right half = Deck B (User2);
       User1 = mixer + FX. Covers the A07 two-track transition.
- D03: launch in DECKS; never-pressed/unused/re-entered/reconnected pads show
       dim (mapped) or off (unused); LEDs follow press state, not Mixxx state.
- D04: symmetric +/-1% per 20 ms, first step on first tick (tap <20 ms =
  no change); both pads held -> last-press wins; release cancels.

Pad addressing: grid pads are identified as (row, col) 0-based, row 0 = TOP.
Converted to Session-layout MIDI notes via protocol.grid_note_zero_based.
Top-row selectors are CC_USER1 / CC_USER2 (protocol).
"""
from dataclasses import dataclass
from enum import Enum

from . import protocol as P


class ProfileId(Enum):
    MIXER_FX = "mixer_fx"  # physical User 1
    DECKS = "decks"        # physical User 2


class ControlType(Enum):
    BUTTON = "button"  # 1 yellow pad, one action per press
    KNOB = "knob"      # 3 pads: red(-) yellow(reset) green(+)
    FADER = "fader"    # 2 pads: red(-) green(+)  -- D01 resolution


@dataclass(frozen=True)
class PadBinding:
    pad: int            # MIDI note (grid) — unique within profile
    row: int
    col: int
    control_id: str     # logical id, e.g. "deckA.play"
    ctype: ControlType
    role: str           # "inc" | "dec" | "reset" | "trigger"
    color: str          # "red" | "green" | "yellow"
    mixxx_group: str    # e.g. "[Channel1]"
    mixxx_key: str      # e.g. "play"


@dataclass
class Profile:
    pid: ProfileId
    bindings: list  # list[PadBinding]

    def by_pad(self, pad: int):
        for b in self.bindings:
            if b.pad == pad:
                return b
        return None


def _note(r, c):
    return P.grid_note_zero_based(r, c)


def _knob(control_id, group, key, r, c, default=50.0):
    """Three adjacent pads: (r,c)=dec red, (r,c+1)=reset yellow, (r,c+2)=inc green."""
    return [
        PadBinding(_note(r, c), r, c, control_id, ControlType.KNOB, "dec", "red", group, key),
        PadBinding(_note(r, c + 1), r, c + 1, control_id, ControlType.KNOB, "reset", "yellow", group, key),
        PadBinding(_note(r, c + 1 + 1), r, c + 1 + 1, control_id, ControlType.KNOB, "inc", "green", group, key),
    ]


def _fader(control_id, group, key, r, c):
    """Two adjacent pads: (r,c)=dec red, (r,c+1)=inc green. D01."""
    return [
        PadBinding(_note(r, c), r, c, control_id, ControlType.FADER, "dec", "red", group, key),
        PadBinding(_note(r, c + 1), r, c + 1, control_id, ControlType.FADER, "inc", "green", group, key),
    ]


def _btn(control_id, group, key, r, c):
    return [PadBinding(_note(r, c), r, c, control_id, ControlType.BUTTON, "trigger", "yellow", group, key)]


def build_decks_profile() -> Profile:
    b = []
    # Deck A (left half, cols 0-3), Deck B mirror (cols 4-7).
    for deck, grp, c0 in (("deckA", "[Channel1]", 0), ("deckB", "[Channel2]", 4)):
        b += _btn(f"{deck}.load", grp, "LoadSelectedTrack", 0, c0)
        b += _btn(f"{deck}.play", grp, "play", 0, c0 + 1)
        b += _btn(f"{deck}.cue", grp, "cue_default", 0, c0 + 2)
        b += _btn(f"{deck}.sync", grp, "beatsync", 0, c0 + 3)
        b += _knob(f"{deck}.gain", grp, "pregain", 1, c0)
        # (1,c0+3) would overflow the half; rate knob sits on row 2.
        b += _knob(f"{deck}.rate", grp, "rate", 2, c0)
        b += _knob(f"{deck}.filter", grp, "filterHigh", 3, c0)
        b += _btn(f"{deck}.pfl", grp, "pfl", 4, c0 + 1)
    # Shared crossfader at bottom centre.
    b += _fader("mixer.crossfader", "[Master]", "crossfader", 7, 3)
    # Shared phones mix + master cue as buttons.
    b += _btn("mixer.headmix", "[Master]", "headMix", 7, 0)
    b += _btn("mixer.headcue", "[Master]", "headSplit", 7, 6)
    return Profile(ProfileId.DECKS, b)


def build_mixer_fx_profile() -> Profile:
    b = []
    b += _fader("mixer.ch1", "[Channel1]", "volume", 0, 0)
    b += _fader("mixer.ch2", "[Channel2]", "volume", 0, 3)
    b += _fader("mixer.crossfader", "[Master]", "crossfader", 0, 6)
    b += _btn("mixer.mute1", "[Channel1]", "mute", 1, 0)
    b += _btn("mixer.mute2", "[Channel2]", "mute", 1, 1)
    b += _btn("mixer.pfl1", "[Channel1]", "pfl", 1, 3)
    b += _btn("mixer.pfl2", "[Channel2]", "pfl", 1, 4)
    b += _knob("mixer.master", "[Master]", "gain", 2, 0)
    b += _knob("mixer.headmix", "[Master]", "headMix", 2, 4)
    b += _knob("fx.mix", "[EffectRack1_EffectUnit1]", "mix", 4, 0)
    b += _knob("fx.param", "[EffectRack1_EffectUnit1_Effect1]", "parameter1", 4, 4)
    b += _btn("fx.enable1", "[EffectRack1_EffectUnit1]", "enable", 6, 0)
    b += _btn("fx.enableA", "[EffectRack1_EffectUnit1]", "group_[Channel1]_enable", 6, 1)
    b += _btn("fx.enableB", "[EffectRack1_EffectUnit1]", "group_[Channel2]_enable", 6, 2)
    return Profile(ProfileId.MIXER_FX, b)


PROFILES = {
    ProfileId.DECKS: build_decks_profile(),
    ProfileId.MIXER_FX: build_mixer_fx_profile(),
}


def validate(profiles=PROFILES) -> list:
    """Mapping contract checks (PLAN). Returns list of error strings."""
    errors = []
    for pid, prof in profiles.items():
        pads = [x.pad for x in prof.bindings]
        if len(pads) != len(set(pads)):
            errors.append(f"{pid.value}: duplicate pad addresses")
        # control pad counts
        by_ctrl: dict = {}
        for x in prof.bindings:
            by_ctrl.setdefault(x.control_id, []).append(x)
        for cid, xs in by_ctrl.items():
            t = xs[0].ctype
            want = {ControlType.BUTTON: 1, ControlType.KNOB: 3, ControlType.FADER: 2}[t]
            if len(xs) != want:
                errors.append(f"{pid.value}/{cid}: {t.value} has {len(xs)} pads, want {want}")
            cols = {x.color for x in xs}
            if t == ControlType.KNOB and cols != {"red", "yellow", "green"}:
                errors.append(f"{pid.value}/{cid}: knob colours {cols}")
            if t == ControlType.FADER and cols != {"red", "green"}:
                errors.append(f"{pid.value}/{cid}: fader colours {cols} (D01)")
            if t == ControlType.BUTTON and (len(xs) != 1 or xs[0].color != "yellow"):
                errors.append(f"{pid.value}/{cid}: button must be 1 yellow pad")
    # capacity: 64 grid pads + 2 selectors reserved (top-row CCs not in grid space)
    for pid, prof in profiles.items():
        if len(prof.bindings) > 64:
            errors.append(f"{pid.value}: exceeds 64 grid pads")
    return errors
