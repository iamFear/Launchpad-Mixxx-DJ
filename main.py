"""Entry points: emulator GUI (no hardware needed) or live MK2 mode.

Usage:
  PYTHONPATH=src python3 main.py --emulator   # on-screen Launchpad -> Mixxx
  PYTHONPATH=src python3 main.py              # physical MK2 (needs hardware)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def main(argv: list) -> int:
    if "--emulator" in argv:
        from launchpad_mixxx.emulator import main as emu_main
        emu_main()
        return 0
    from launchpad_mixxx.app import DjApp
    from launchpad_mixxx.endpoints import CoreMidiLaunchpad, FakeMixxx
    try:
        hw = CoreMidiLaunchpad()
        hw.open()
    except RuntimeError as e:
        print(f"Live mode unavailable: {e}")
        print("Run the emulator instead: PYTHONPATH=src python3 main.py --emulator")
        print("Tests: python3 -m pytest tests/ -q")
        return 2
    app = DjApp(launchpad=hw, mixxx=FakeMixxx())
    print(f"Bridge running, profile={app.router.active.value}. Ctrl-C to quit.")
    import time
    try:
        while True:
            time.sleep(0.02)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
