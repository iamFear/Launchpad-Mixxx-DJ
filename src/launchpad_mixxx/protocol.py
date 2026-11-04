"""Novation Launchpad MK2 protocol constants.

Source: Novation "Launchpad MK2 Programmers Reference Manual v1.03"
(fael-downloads-prod.focusrite.com). Values below are distilled from that
document; physical LED palette calibration is still open (see docs/DECISIONS.md
D03) because no MK2 was available during the hackathon build.
"""

SYSEX_HEADER = (0xF0, 0x00, 0x20, 0x29, 0x02, 0x18)

LAYOUT_SESSION = 0x00
LAYOUT_USER1 = 0x01
LAYOUT_USER2 = 0x02

SESSION_CHANNEL = 0  # 0-based: MIDI channel 1
USER1_CHANNELS = (5, 6, 7)  # bootloader-selectable ch 6-8 (0-based 5-7)
USER2_CHANNELS = (13, 14, 15)  # ch 14-16 (0-based 13-15)

FLASH_CHANNEL_OFFSET = 1  # channel 2 behaviour: flash
PULSE_CHANNEL_OFFSET = 2  # channel 3 behaviour: pulse

# Top-row round buttons are always CC 104..111 regardless of layout.
# Order left->right assumed from the reference figures:
# Up, Down, Left, Right, Session, User1, User2, Mixer.
CC_TOP_ROW = tuple(range(104, 112))
CC_SESSION = 108
CC_USER1 = 109
CC_USER2 = 110
CC_MIXER = 111


def session_note(row: int, col: int) -> int:
    """Session/User2 grid note: row*10+col, row 1 at bottom, col 9 = scene.

    Bottom-left pad = 11, top-right grid pad = 88. `row`/`col` here are
    1-based to match the manual. The app uses 0-based (r, c) elsewhere and
    converts via this helper.
    """
    return row * 10 + col


def grid_note_zero_based(r: int, c: int) -> int:
    """0-based (r, c) with r=0 at TOP to MIDI note (Session layout)."""
    return (8 - r) * 10 + (c + 1)


def layout_select_message(layout: int) -> tuple:
    return SYSEX_HEADER + (0x22, layout, 0xF7)


# Provisional LED palette (velocity values). The manual defines colour by
# velocity 0..127 (0 = off) plus RGB SysEx mode. Exact dim/bright palette
# entries must be calibrated against a physical MK2 (T01) — these are
# centralised here so calibration is a one-spot change.
LED_OFF = 0
PALETTE = {
    ("red", "dim"): 1,
    ("red", "bright"): 5,
    ("green", "dim"): 17,
    ("green", "bright"): 21,
    ("yellow", "dim"): 9,
    ("yellow", "bright"): 13,
}
