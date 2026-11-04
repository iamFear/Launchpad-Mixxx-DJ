"""Build docs/Launchpad-Mixxx-DJ-Manual.pdf from the code (single source of truth).

Run:  PYTHONPATH=src python3 docs/build_manual.py
Requires: fpdf2 (pip install -r requirements.txt)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fpdf import FPDF

from launchpad_mixxx.mapping import PROFILES, ProfileId

FILL = {"red": (120, 20, 20), "green": (20, 120, 20), "yellow": (150, 125, 0)}
ROLE_GLYPH = {"trigger": "", "inc": " ^", "dec": " v", "reset": " ="}


def short_label(b) -> str:
    name = b.control_id.split(".")[-1]
    keep = {"load": "LOAD", "play": "PLAY", "cue": "CUE", "sync": "SYNC",
            "pfl": "PFL", "pfl1": "PFL1", "pfl2": "PFL2", "mute1": "MUT1",
            "mute2": "MUT2", "ch1": "CH1", "ch2": "CH2", "master": "MAST",
            "headmix": "HMIX", "headcue": "HPHN", "crossfader": "XF",
            "gain": "GAIN", "rate": "RATE", "filter": "FLT", "mix": "MIX",
            "param": "PRM", "enable1": "FX", "enableA": "FX>A", "enableB": "FX>B"}
    return keep.get(name, name.upper()[:4])


class Manual(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "Launchpad-Mixxx-DJ User Manual", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}", align="C")

    def h1(self, t):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(10, 10, 10)
        self.multi_cell(0, 9, t, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def h2(self, t):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 7, t, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, t):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(10, 10, 10)
        self.multi_cell(0, 5.5, t, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def bullets(self, items):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(10, 10, 10)
        for it in items:
            self.multi_cell(0, 5.5, "  -  " + it, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def steps(self, items):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(10, 10, 10)
        for i, it in enumerate(items, 1):
            self.multi_cell(0, 5.5, f"  {i}. {it}", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def grid_diagram(self, pid: ProfileId):
        bypos = {(b.row, b.col): b for b in PROFILES[pid].bindings}
        cw, chh = 21.5, 13
        x0 = (210 - 8 * cw) / 2
        y0 = self.get_y() + 2
        for r in range(8):
            for c in range(8):
                x, y = x0 + c * cw, y0 + r * chh
                b = bypos.get((r, c))
                if b is None:
                    self.set_fill_color(35, 35, 35)
                    self.rect(x, y, cw - 0.6, chh - 0.6, "F")
                else:
                    self.set_fill_color(*FILL[b.color])
                    self.rect(x, y, cw - 0.6, chh - 0.6, "F")
                    self.set_xy(x, y + 1.5)
                    self.set_font("Helvetica", "B", 6.5)
                    self.set_text_color(255, 255, 255)
                    self.cell(cw - 0.6, 4, short_label(b) + ROLE_GLYPH[b.role], align="C")
                    self.set_xy(x, y + 6.5)
                    self.set_font("Helvetica", "", 5.5)
                    self.cell(cw - 0.6, 4, b.ctype.value, align="C")
        self.set_y(y0 + 8 * chh + 4)
        self.set_text_color(10, 10, 10)

    def pad_table(self, pid: ProfileId):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(230, 230, 230)
        for w, t in ((18, "Pad"), (42, "Control"), (22, "Type"),
                     (28, "Action"), (18, "LED"), (62, "Mixxx target")):
            self.cell(w, 6, t, border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 8.5)
        for b in sorted(PROFILES[pid].bindings, key=lambda x: (x.row, x.col)):
            action = {"trigger": "press once", "inc": "hold: +1%/20ms",
                      "dec": "hold: -1%/20ms", "reset": "reset 50%"}[b.role]
            row = [f"R{b.row}C{b.col}", b.control_id, b.ctype.value,
                   action, b.color, f"{b.mixxx_group} {b.mixxx_key}"]
            h = 6
            if self.get_y() + h > 275:
                self.add_page()
            for w, t in zip((18, 42, 22, 28, 18, 62), row):
                self.cell(w, h, t, border=1)
            self.ln()
        self.ln(2)


def build(path: str) -> int:
    pdf = Manual()
    pdf.alias_nb_pages("{nb}")
    pdf.set_auto_page_break(True, 15)
    pdf.set_margins(15, 12, 15)

    # Cover
    pdf.add_page()
    pdf.ln(45)
    pdf.set_font("Helvetica", "B", 28)
    pdf.multi_cell(0, 13, "Launchpad-Mixxx-DJ", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 9, "Play a full DJ set in Mixxx with one Novation Launchpad MK2", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, "User Manual  |  Meta Hackathon  |  Mixxx 2.5.x  |  macOS", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.multi_cell(0, 7, "Covers: installation, Mixxx setup, emulator tour, both pad maps, your first transition, hardware mode, troubleshooting.", align="C", new_x="LMARGIN", new_y="NEXT")

    # 1. What this is
    pdf.add_page()
    pdf.h1("1. What this is")
    pdf.body("Launchpad-Mixxx-DJ turns a single Novation Launchpad MK2 into two CDJ-style "
             "decks plus a mixer and FX unit for Mixxx (2.5.x) on macOS. Mixxx stays in charge "
             "of all audio; the app translates pad presses into Mixxx commands over MIDI and "
             "drives the pad LEDs. No DJ controller hardware is required: the app ships an "
             "on-screen emulator that drives Mixxx while it is open.")
    pdf.bullets([
        "Two profiles: User 2 = decks (Deck A left, Deck B right). User 1 = mixer + FX.",
        "Green = increase, red = decrease (hold: 1% per 20 ms). Yellow = one action per press.",
        "Knobs use 3 pads (down / reset-to-centre / up); faders use 2 pads (down / up).",
        "Held pads glow bright; released pads glow dim in their colour.",
    ])

    # 2. Install
    pdf.h1("2. Installation")
    pdf.h2("Requirements")
    pdf.bullets(["macOS with Python 3.11+ (tkinter included)", "Mixxx 2.5.x",
                 "Novation Launchpad MK2 only if using hardware mode"])
    pdf.h2("Steps")
    pdf.steps([
        "Unzip the release and open a Terminal in the project folder.",
        "Create a virtual environment: python3 -m venv .venv && source .venv/bin/activate",
        "Install dependencies: pip install -r requirements.txt",
        "Sanity check: python3 -m pytest tests/ -q (expect 16 passed).",
    ])

    # 3. Mixxx setup
    pdf.add_page()
    pdf.h1("3. Connecting Mixxx (one time)")
    pdf.steps([
        "Copy mixxx_mapping/LaunchpadMK2Bridge.midi.xml into Mixxx's user controllers folder. "
        "On macOS (Mixxx 2.5): ~/Library/Containers/org.mixxx.mixxx/Data/Library/"
        "Application Support/Mixxx/controllers/ (create it if missing).",
        "Start the emulator (section 4) so Mixxx can see the virtual port.",
        "In Mixxx: Preferences > Controllers > select the LaunchpadMK2Bridge device.",
        "Enable it and choose the 'Launchpad MK2 DJ Bridge' mapping, then OK.",
        "If the device is missing, close and reopen Preferences while the emulator runs.",
    ])
    pdf.body("Technical note: the mapping is declarative XML (notes for buttons, CCs for "
             "continuous controls). The app owns all repeat and profile logic; Mixxx only "
             "receives commands and plays audio.")

    # 4. Emulator tour
    pdf.add_page()
    pdf.h1("4. Emulator tour")
    pdf.body("Launch it with:  PYTHONPATH=src python3 main.py --emulator")
    pdf.bullets([
        "Top row: Session / User 1 / User 2 / Mixer. User 1 selects mixer+FX, User 2 selects decks. The active one glows.",
        "Main 8x8 grid: click-and-hold pads exactly like hardware. Row 0 is the top row.",
        "Profile label under the top row tells you which layout is active.",
        "Right panel: connection status plus a live log of every command sent to Mixxx, "
        "e.g. [Channel1] play 1.00 or [Master] crossfader 0.57.",
        "MIDI live means the CoreMIDI virtual port is open and Mixxx can hear it.",
    ])
    pdf.h2("Clicking technique")
    pdf.bullets([
        "Buttons: single click = one action. Holding does nothing extra; release re-arms.",
        "Knobs/faders: press AND HOLD the green (up) or red (down) pad; value moves 1% per 20 ms.",
        "Yellow pad inside a knob = snap that control back to centre (50%).",
        "Switching profiles or releasing cancels any in-progress hold.",
    ])

    # 5. Decks
    pdf.add_page()
    pdf.h1("5. Decks profile (User 2)")
    pdf.body("Deck A owns columns 0-3 ([Channel1]), Deck B mirrors it on columns 4-7 "
             "([Channel2]). Bottom row holds shared crossfader and headphone controls.")
    pdf.grid_diagram(ProfileId.DECKS)
    pdf.pad_table(ProfileId.DECKS)

    # 6. Mixer/FX
    pdf.add_page()
    pdf.h1("6. Mixer + FX profile (User 1)")
    pdf.body("Channel faders, mutes, cue buttons, master/headphone knobs, FX mix and "
             "parameter knobs, and FX routing buttons.")
    pdf.grid_diagram(ProfileId.MIXER_FX)
    pdf.pad_table(ProfileId.MIXER_FX)

    # 7. First transition
    pdf.add_page()
    pdf.h1("7. Your first transition (step by step)")
    pdf.steps([
        "Load two tracks into Mixxx's library (Auto DJ / crates).",
        "User 2 profile. Deck A: click LOAD, then PLAY. Track A starts.",
        "Deck B: click LOAD, then CUE, then SYNC to match tempo, then PLAY.",
        "Hold the crossfader ^ pad (row 7) for ~2 seconds to sweep fully from A to B.",
        "Press User 1. Click FX>B to route the effect to Deck B, then click FX to enable it.",
        "Hold FX MIX ^ for ~1 second to bring the effect in. Adjust FX PRM to taste.",
        "Press User 2 to return to the decks and continue mixing. Repeat for every transition.",
    ])
    pdf.body("Tip: short taps under 20 ms do nothing by design (below one repeat tick). "
             "Deliberate holds of 50-150 ms give fine 2-7% nudges.")

    # 8. Hardware
    pdf.h1("8. Physical Launchpad mode")
    pdf.steps([
        "Quit the emulator. Plug in the Launchpad MK2 (Session layout).",
        "Run: PYTHONPATH=src python3 main.py (hardware path; the physical",
        "T01 spike still has to be run against a real MK2 - the emulator is",
        "the supported route until then).",
        "Physical User 1 / User 2 buttons switch profiles; the app redraws the LEDs.",
        "Everything else behaves exactly like the emulator, including colours.",
    ])

    # 9. Troubleshooting
    pdf.h1("9. Troubleshooting")
    pdf.bullets([
        "Mixxx doesn't react: mapping not installed/enabled (section 3); Preferences opened before the emulator started.",
        "Two LaunchpadMK2Bridge ports listed: an old emulator instance is still running; quit it.",
        "Value jumps on first touch: by design the app owns 0-100% state and Mixxx follows (no soft-takeover in v1).",
        "LED colours look wrong: dim/bright palette needs calibration against a real MK2 (single spot in protocol.py).",
        "Emulator says MIDI unavailable: not on macOS or CoreMIDI denied; commands still logged.",
    ])

    # 10. Appendix
    pdf.add_page()
    pdf.h1("10. Appendix")
    pdf.h2("Timing contract")
    pdf.body("Knob/fader holds step on a 20 ms tick: 1% at 20 ms, 50% at 1 s, 100% at 2 s "
             "from 0%, clamped at both ends. Symmetric for decrease. If both direction pads "
             "are held, the last press wins; release cancels the hold. Buttons fire once per press.")
    pdf.h2("Verification status")
    pdf.body("16/16 deterministic tests pass (fake clock and fake endpoints). Physical acceptance "
             "runs on a real MK2 with live Mixxx are recorded as Blocked in docs/VERIFICATION.md "
             "until hardware timing (scheduling jitter, LED palette) is measured.")
    pdf.h2("Files")
    pdf.bullets([
        "src/launchpad_mixxx/: protocol, clock, mapping, engine, router, leds, endpoints, coremidi_bridge, app, emulator.",
        "mixxx_mapping/LaunchpadMK2Bridge.midi.xml: generated from the code mapping.",
        "tests/: knob engine, routing/LEDs/acceptance, emulator + live sender.",
        "docs/: DECISIONS.md, SETUP.md, EMULATOR.md, VERIFICATION.md.",
        "agents/: SPEC.md, PLAN.md, TASKS.md, ACCEPTANCE.md (build contract).",
    ])

    pdf.output(path)
    return pdf.page_no()


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "Launchpad-Mixxx-DJ-Manual.pdf")
    n = build(out)
    print(f"wrote {out} ({n} pages, {os.path.getsize(out)//1024} KB)")
