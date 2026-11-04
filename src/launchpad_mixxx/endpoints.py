"""Hardware + Mixxx endpoints. Fakes for tests; MIDI bridge for live use.

Launchpad endpoint: owns device-specific MIDI (protocol.py). The live
implementation needs `mido` + a CoreMIDI backend (python-rtmidi) and a
physical MK2 — unavailable in this build, so `CoreMidiLaunchpad` documents
the wiring and raises a clear error; `FakeLaunchpad` records LED writes and
replays scripted pad events for deterministic tests and the simulator.

Mixxx endpoint: translates LogicalAction -> Mixxx group/key + bridge MIDI
message. Live path = virtual CoreMIDI port the app writes; Mixxx learns it
via mixxx_mapping/LaunchpadMK2.midi.xml (Mixxx 2.5, schemaVersion 1).
`FakeMixxx` records commands for acceptance evidence.
"""
from . import protocol as P
from .model import LedState, LogicalAction


class FakeLaunchpad:
    def __init__(self):
        self.led_writes: list = []  # LedState
        self.layout = P.LAYOUT_SESSION
        self.connected = True

    def set_led(self, led: LedState):
        self.led_writes.append(led)

    def set_layout(self, layout: int):
        self.layout = layout

    def disconnect(self):
        self.connected = False

    def reconnect(self):
        self.connected = True


class CoreMidiLaunchpad:
    """Live MK2 wiring (requires hardware + `mido[rtmidi]`).

    Grid: note-on vel 127 = press, vel 0 = release (channel per layout;
    Session = ch 1). LEDs: note-on velocity = palette colour (protocol.py).
    Top row: CC 104..111, 127 press / 0 release. Layout via SysEx
    F0 00 20 29 02 18 22 <layout> F7.
    """

    def __init__(self, port_name="Launchpad MK2", mido_module=None):
        if mido_module is None:
            try:
                import mido  # type: ignore
                mido_module = mido
            except ImportError as e:
                raise RuntimeError(
                    "Live Launchpad access needs `pip install mido python-rtmidi` "
                    "on macOS with a physical MK2 connected."
                ) from e
        self._mido = mido_module
        self.port_name = port_name

    def open(self):
        ins = self._mido.get_input_names()
        outs = self._mido.get_output_names()
        hit = [n for n in ins + outs if "Launchpad" in n or "MK2" in n]
        raise RuntimeError(
            f"No live run without hardware. MIDI ports seen: inputs={ins} "
            f"outputs={outs} matched={hit}. Connect an MK2 and retry."
        )


# ---------------------------------------------------------------- Mixxx ---
# Bridge MIDI vocabulary (app -> Mixxx virtual port). Ch 1 notes for buttons,
# Ch 1 CCs for continuous values 0..127. The XML mapping binds these.
BRIDGE_CHANNEL = 0


def bridge_message_for(action: LogicalAction, control_index: int):
    """Deterministic bridge message for a logical action.

    Returns ("note", no, vel) for buttons/reset, ("cc", no, val) for
    continuous. control_index comes from MIXXX_CONTROLS order.
    """
    if action.kind == "button" or (action.kind == "knob" and action.direction == 0):
        vel = 127
        return ("note", 0x30 + (control_index % 64), vel)
    val = int(round((action.value01 or 0.0) * 127))
    return ("cc", 0x10 + (control_index % 64), val)


# control_id -> (group, key, kind-hint)
MIXXX_CONTROLS = {
    "deckA.load": ("[Channel1]", "LoadSelectedTrack"),
    "deckA.play": ("[Channel1]", "play"),
    "deckA.cue": ("[Channel1]", "cue_default"),
    "deckA.sync": ("[Channel1]", "beatsync"),
    "deckA.gain": ("[Channel1]", "pregain"),
    "deckA.rate": ("[Channel1]", "rate"),
    "deckA.filter": ("[Channel1]", "filterHigh"),
    "deckA.pfl": ("[Channel1]", "pfl"),
    "deckB.load": ("[Channel2]", "LoadSelectedTrack"),
    "deckB.play": ("[Channel2]", "play"),
    "deckB.cue": ("[Channel2]", "cue_default"),
    "deckB.sync": ("[Channel2]", "beatsync"),
    "deckB.gain": ("[Channel2]", "pregain"),
    "deckB.rate": ("[Channel2]", "rate"),
    "deckB.filter": ("[Channel2]", "filterHigh"),
    "deckB.pfl": ("[Channel2]", "pfl"),
    "mixer.ch1": ("[Channel1]", "volume"),
    "mixer.ch2": ("[Channel2]", "volume"),
    "mixer.crossfader": ("[Master]", "crossfader"),
    "mixer.master": ("[Master]", "gain"),
    "mixer.headmix": ("[Master]", "headMix"),
    "mixer.headcue": ("[Master]", "headSplit"),
    "mixer.mute1": ("[Channel1]", "mute"),
    "mixer.mute2": ("[Channel2]", "mute"),
    "mixer.pfl1": ("[Channel1]", "pfl"),
    "mixer.pfl2": ("[Channel2]", "pfl"),
    "fx.mix": ("[EffectRack1_EffectUnit1]", "mix"),
    "fx.param": ("[EffectRack1_EffectUnit1_Effect1]", "parameter1"),
    "fx.enable1": ("[EffectRack1_EffectUnit1]", "enable"),
    "fx.enableA": ("[EffectRack1_EffectUnit1]", "group_[Channel1]_enable"),
    "fx.enableB": ("[EffectRack1_EffectUnit1]", "group_[Channel2]_enable"),
}


class FakeMixxx:
    """Records commands; never sends audio-affecting state back into LEDs."""

    def __init__(self):
        self.commands: list = []  # (group, key, value01_or_trigger, bridge_msg)

    def send(self, action: LogicalAction):
        group, key = MIXXX_CONTROLS.get(action.control_id, ("[Master]", action.control_id))
        idx = sorted(MIXXX_CONTROLS).index(action.control_id) if action.control_id in MIXXX_CONTROLS else 0
        msg = bridge_message_for(action, idx)
        payload = action.value01 if action.value01 is not None else 1.0
        self.commands.append((group, key, payload, msg))
        return (group, key, payload, msg)


def generate_mixxx_xml() -> str:
    """Build the Mixxx 2.5 XML mapping for the bridge vocabulary."""
    lines = ['<?xml version="1.0" encoding="utf-8"?>',
             '<MixxxControllerPreset schemaVersion="1" mixxxVersion="2.5.0">',
             " <info>",
             "  <name>Launchpad MK2 DJ Bridge</name>",
             "  <author>Meta Hackathon</author>",
             "  <description>Auto-generated bridge mapping: app virtual port drives decks/mixer/FX. Install per docs/SETUP.md.</description>",
             " </info>",
             ' <controller id="LaunchpadMK2Bridge">', "  <controls>"]
    for i, cid in enumerate(sorted(MIXXX_CONTROLS)):
        group, key = MIXXX_CONTROLS[cid]
        is_button = cid.split(".")[-1] in (
            "load", "play", "cue", "sync", "pfl", "pfl1", "pfl2",
            "mute1", "mute2", "enable1", "enableA", "enableB", "headcue",
        )
        if is_button:
            status, midino = "0x90", hex(0x30 + (i % 64))
            opts = "            <options><normal/></options>"
        else:
            status, midino = "0xB0", hex(0x10 + (i % 64))
            opts = "            <options><normal/></options>"
        lines += ["   <control>",
                  f"    <group>{group}</group>", f"    <key>{key}</key>",
                  f"    <status>{status}</status>", f"    <midino>{midino}</midino>",
                  opts, "   </control>"]
    lines += ["  </controls>", " </controller>", "</MixxxControllerPreset>"]
    return "\n".join(lines) + "\n"
