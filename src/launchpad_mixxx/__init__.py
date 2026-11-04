"""Launchpad MK2 -> Mixxx bridge (Meta hackathon).

Keeps Mixxx in charge of audio. Raw MIDI lives at the hardware boundary
(`protocol.py`, `launchpad.py`); Mixxx control identifiers live at the
integration boundary (`mixxx.py`). Everything between them uses logical
controls from `mapping.py` so unit tests run with fakes and no hardware.
"""
from .app import DjApp, build_default_app
from .mapping import PROFILES, ProfileId

__all__ = ["DjApp", "build_default_app", "PROFILES", "ProfileId"]
