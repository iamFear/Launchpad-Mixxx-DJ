"""Live entry: boots the bridge against a real MK2 + Mixxx (needs hardware).

Without hardware it prints what is missing and points at the simulator.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from launchpad_mixxx.app import DjApp
from launchpad_mixxx.endpoints import CoreMidiLaunchpad, FakeLaunchpad, FakeMixxx


def main():
    try:
        hw = CoreMidiLaunchpad()
        hw.open()
    except RuntimeError as e:
        print(f"Live mode unavailable: {e}")
        print("Run the simulation instead: PYTHONPATH=src python3 simulator.py")
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
    raise SystemExit(main())
