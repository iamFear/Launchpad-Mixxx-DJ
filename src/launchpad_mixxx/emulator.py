"""On-screen Launchpad MK2 emulator (tkinter, stdlib only).

Looks and behaves like the hardware grid: 8x8 pads + top-row profile
buttons. Mouse press/release flows through the real DjApp
(router -> engine -> Mixxx sender), and pad colours follow the LED renderer
(bright while held, dim after release). Every action is ALSO sent to Mixxx
over the CoreMIDI virtual port, so the emulator drives Mixxx while it is
open — no physical Launchpad needed.

Run:  PYTHONPATH=src python3 main.py --emulator
"""
import time
import tkinter as tk

from . import protocol as P
from .app import DjApp
from .endpoints import FakeMixxx, LiveMixxxSender
from .mapping import ProfileId
from .model import PadEvent

# tkinter approximations of dim/bright MK2 palette entries.
COLORS = {
    ("red", "dim"): "#5a1010", ("red", "bright"): "#ff3030",
    ("green", "dim"): "#0e4d0e", ("green", "bright"): "#28e028",
    ("yellow", "dim"): "#5a4d00", ("yellow", "bright"): "#ffe128",
    ("off", "off"): "#161616",
}
FG = {"bright": "#000000", "dim": "#ffffff", "off": "#555555"}

TOP_BUTTONS = [("Session", P.CC_SESSION), ("User 1", P.CC_USER1),
               ("User 2", P.CC_USER2), ("Mixer", P.CC_MIXER)]


def pad_label(binding) -> str:
    short = binding.control_id.split(".")[-1]
    if binding.role == "trigger":
        return short[:6]
    return {"inc": "▲", "dec": "▼", "reset": "="}[binding.role]


def led_colors(led) -> tuple:
    return COLORS.get((led.color, led.brightness), COLORS[("off", "off")]), \
        FG.get(led.brightness, "#ffffff")


def now_ms() -> int:
    return int(time.monotonic() * 1000)


class Emulator:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Launchpad MK2 Emulator → Mixxx")
        try:
            sender: FakeMixxx = LiveMixxxSender()
        except Exception:  # noqa: BLE001
            sender = FakeMixxx()
        if isinstance(sender, LiveMixxxSender) and not sender.live:
            sender = FakeMixxx()
        self.sender = sender
        self.app = DjApp(mixxx=sender)
        self.t0 = now_ms()
        self.pad_btn: dict = {}
        self.top_btn: dict = {}

        top = tk.Frame(root)
        top.pack(pady=4)
        for name, cc in TOP_BUTTONS:
            b = tk.Button(top, text=name, width=8, font=("Helvetica", 10, "bold"))
            b.pack(side=tk.LEFT, padx=3)
            b.bind("<ButtonPress-1>", lambda e, c=cc: self._top(c, True))
            b.bind("<ButtonRelease-1>", lambda e, c=cc: self._top(c, False))
            self.top_btn[cc] = b

        self.profile_var = tk.StringVar()
        tk.Label(root, textvariable=self.profile_var,
                 font=("Helvetica", 11, "bold")).pack()

        body = tk.Frame(root)
        body.pack()
        grid = tk.Frame(body)
        grid.pack(side=tk.LEFT, padx=8)
        self.grid_btns: list = []
        for r in range(8):
            row = []
            for c in range(8):
                b = tk.Button(grid, text="", width=5, height=2, font=("Helvetica", 7))
                b.grid(row=r, column=c, padx=1, pady=1)
                b.bind("<ButtonPress-1>", lambda e, r=r, c=c: self._press(r, c))
                b.bind("<ButtonRelease-1>", lambda e, r=r, c=c: self._release(r, c))
                row.append(b)
            self.grid_btns.append(row)

        side = tk.Frame(body)
        side.pack(side=tk.LEFT, fill=tk.Y, padx=8)
        midi_txt = ("MIDI live → Mixxx on 'LaunchpadMK2Bridge'"
                    if getattr(sender, "live", False)
                    else "MIDI unavailable (record-only)")
        tk.Label(side, text=midi_txt, font=("Helvetica", 10)).pack(anchor="w")
        tk.Label(side, text="Mixxx commands:", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.log = tk.Listbox(side, width=44, height=24, font=("Menlo", 9))
        self.log.pack(fill=tk.BOTH, expand=True)
        self._seen_logs = 0

        self.redraw()
        self.root.after(20, self._tick)

    # -- events ------------------------------------------------------
    def _pad_note(self, r: int, c: int) -> int:
        from .protocol import grid_note_zero_based
        return grid_note_zero_based(r, c)

    def _press(self, r: int, c: int):
        self.app.pad_event(PadEvent(self._pad_note(r, c), False, True), now_ms())
        self.redraw()
        self._drain_log()

    def _release(self, r: int, c: int):
        self.app.pad_event(PadEvent(self._pad_note(r, c), False, False), now_ms())
        self.redraw()
        self._drain_log()

    def _top(self, cc: int, pressed: bool):
        self.app.pad_event(PadEvent(cc, True, pressed), now_ms())
        self.redraw()
        self._drain_log()

    def _tick(self):
        self.app.tick(now_ms())
        self._drain_log()
        self.root.after(20, self._tick)

    # -- view --------------------------------------------------------
    def redraw(self):
        prof = self.app.router.profile
        by_pad = {b.pad: b for b in prof.bindings}
        held = self.app.leds.held
        for r in range(8):
            for c in range(8):
                note = self._pad_note(r, c)
                btn = self.grid_btns[r][c]
                b = by_pad.get(note)
                if b is None:
                    btn.configure(text="", bg=COLORS[("off", "off")], fg=FG["off"])
                else:
                    bright = "bright" if note in held else "dim"
                    btn.configure(text=pad_label(b),
                                  bg=COLORS[(b.color, bright)], fg=FG[bright])
        active = self.app.router.active
        self.profile_var.set(f"Profile: {active.value}  "
                             f"({'decks: A left / B right' if active == ProfileId.DECKS else 'mixer + FX'})")
        for name, cc in TOP_BUTTONS:
            on = ((cc == P.CC_USER1 and active == ProfileId.MIXER_FX) or
                  (cc == P.CC_USER2 and active == ProfileId.DECKS))
            self.top_btn[cc].configure(bg="#ffe128" if on else "#e0e0e0")

    def _drain_log(self):
        cmds = self.sender.commands
        while self._seen_logs < len(cmds):
            g, k, v, _msg = cmds[self._seen_logs]
            self.log.insert(tk.END, f"{g} {k} {v:.2f}" if isinstance(v, float) else f"{g} {k} {v}")
            self._seen_logs += 1
            if self.log.size() > 300:
                self.log.delete(0)
        if cmds:
            self.log.see(tk.END)


def main():
    root = tk.Tk()
    try:  # macOS: promote from background item to foreground app
        from Cocoa import NSApplication, NSApplicationActivationPolicyRegular
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        app.activateIgnoringOtherApps_(True)
    except Exception:  # noqa: BLE001 — non-macOS or missing pyobjc
        pass
    root.lift()
    root.attributes("-topmost", True)
    root.after(1500, lambda: root.attributes("-topmost", False))
    Emulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
