"""Emulator helpers + live MIDI sender (no display needed)."""
import pytest

from launchpad_mixxx.coremidi_bridge import VirtualMidiPort, list_sources
from launchpad_mixxx.emulator import led_colors, pad_label
from launchpad_mixxx.endpoints import LiveMixxxSender, bridge_message_for
from launchpad_mixxx.mapping import PROFILES, ProfileId
from launchpad_mixxx.model import LedState, LogicalAction


def test_pad_labels_and_led_colors():
    b = next(x for x in PROFILES[ProfileId.DECKS].bindings
             if x.control_id == "deckA.play")
    assert pad_label(b) == "play"
    inc = next(x for x in PROFILES[ProfileId.DECKS].bindings
               if x.control_id == "deckA.gain" and x.role == "inc")
    assert pad_label(inc) == "▲"
    bg, fg = led_colors(LedState(11, False, "green", "bright"))
    assert bg.startswith("#") and fg.startswith("#")
    bg2, _ = led_colors(LedState(11, False, "green", "dim"))
    assert bg != bg2  # bright vs dim visually distinct


def test_bridge_message_vocabulary():
    kind, num, val = bridge_message_for(LogicalAction("deckA.play", "button", 0, None, 0), 0)
    assert kind == "note" and val == 127
    kind, num, val = bridge_message_for(LogicalAction("deckA.gain", "knob", 1, 0.5, 0), 3)
    assert kind == "cc" and val == 64


def test_virtual_port_visible_and_live_sender_sends():
    port = VirtualMidiPort("LaunchpadMK2Bridge-Test")
    try:
        assert "LaunchpadMK2Bridge-Test" in list_sources()
        port.send_cc(0, 0x10, 64)
        port.send_note(0, 0x30, 127)
    finally:
        port.close()
    sender = LiveMixxxSender(port_name="LaunchpadMK2Bridge-Test2")
    try:
        assert sender.live, sender.midi_error
        sender.send(LogicalAction("deckA.play", "button", 0, None, 0))
        assert len(sender.commands) == 1
    finally:
        if sender.port is not None:
            sender.port.close()


def test_emulator_press_release_headless():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("no display")
    root.withdraw()
    try:
        from launchpad_mixxx import protocol as P
        from launchpad_mixxx.emulator import Emulator
        from launchpad_mixxx.protocol import grid_note_zero_based
        emu = Emulator(root)
        note = next(x.pad for x in PROFILES[ProfileId.DECKS].bindings
                    if x.control_id == "deckA.play")
        r, c = next((r, c) for r in range(8) for c in range(8)
                    if grid_note_zero_based(r, c) == note)
        emu._press(r, c)
        emu._release(r, c)
        plays = [cm for cm in emu.sender.commands
                 if cm[0] == "[Channel1]" and cm[1] == "play"]
        assert len(plays) == 1
        emu._top(P.CC_USER1, True)
        assert emu.app.router.active == ProfileId.MIXER_FX
    finally:
        root.destroy()
        if getattr(emu.sender, "port", None) is not None:
            emu.sender.port.close()
