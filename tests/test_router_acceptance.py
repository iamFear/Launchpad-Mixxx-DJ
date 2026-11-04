"""A02/A03/A05/A06: routing, LEDs, buttons, profile isolation, stale events."""
from launchpad_mixxx import protocol as P
from launchpad_mixxx.app import DjApp
from launchpad_mixxx.endpoints import FakeLaunchpad, FakeMixxx
from launchpad_mixxx.mapping import PROFILES, ProfileId, validate
from launchpad_mixxx.model import PadEvent


def make_app(**kw):
    return DjApp(launchpad=FakeLaunchpad(), mixxx=FakeMixxx(), **kw)


def grid_pad(pid, control_id, role="trigger"):
    for b in PROFILES[pid].bindings:
        if b.control_id == control_id and b.role == role:
            return b.pad
    raise AssertionError(f"no pad for {control_id}/{role}")


def press(app, pad, top=False, t=0):
    return app.pad_event(PadEvent(pad, top, True), t)


def release(app, pad, top=False, t=0):
    return app.pad_event(PadEvent(pad, top, False), t)


def test_mapping_contract_valid():
    assert validate() == []


def test_button_emits_once_per_press_and_rearms():
    app = make_app()
    pad = grid_pad(ProfileId.DECKS, "deckA.play")
    press(app, pad, t=0)
    press(app, pad, t=5)  # held repeat must not duplicate (P02)
    assert len([c for c in app.mixxx.commands if c[1] == "play"]) == 1
    release(app, pad, t=10)
    press(app, pad, t=20)  # rearms after release (A05)
    assert len([c for c in app.mixxx.commands if c[1] == "play"]) == 2


def test_led_bright_while_held_dim_after_release():
    app = make_app()
    pad = grid_pad(ProfileId.DECKS, "deckA.play")
    press(app, pad, t=0)
    last = [l for l in app.launchpad.led_writes if l.pad == pad][-1]
    assert (last.color, last.brightness) == ("yellow", "bright")
    release(app, pad, t=10)
    last = [l for l in app.launchpad.led_writes if l.pad == pad][-1]
    assert (last.color, last.brightness) == ("yellow", "dim")


def test_profile_switch_preserves_mixxx_and_kills_holds():
    app = make_app(initial_values={"deckA.gain": 20.0})
    inc = grid_pad(ProfileId.DECKS, "deckA.gain", "inc")
    press(app, inc, t=0)
    n_before = len(app.mixxx.commands)
    app.switch_profile(ProfileId.MIXER_FX)  # A06: no commands on switch
    assert len(app.mixxx.commands) == n_before
    app.tick(500)  # old hold must not keep repeating
    assert len(app.mixxx.commands) == n_before
    # delayed release of old pad cannot affect new profile
    release(app, inc, t=600)
    assert len(app.mixxx.commands) == n_before
    # fresh press works afterwards
    assert app.router.active == ProfileId.MIXER_FX


def test_inactive_profile_targets_untouched():
    app = make_app()
    pad = grid_pad(ProfileId.DECKS, "deckA.play")
    press(app, pad, t=0)
    release(app, pad, t=1)
    groups = {c[0] for c in app.mixxx.commands}
    assert "[Channel2]" not in groups  # deck B untouched by deck A press


def test_device_loss_reconnect_restores_leds_sends_nothing():
    app = make_app()
    inc = grid_pad(ProfileId.DECKS, "deckA.gain", "inc")
    press(app, inc, t=0)
    n = len(app.mixxx.commands)
    app.device_lost()
    app.tick(1000)
    assert len(app.mixxx.commands) == n
    app.device_reconnected()
    assert len(app.mixxx.commands) == n
    leds = [l for l in app.launchpad.led_writes if l.pad == inc]
    assert leds and leds[-1].brightness == "dim"  # fresh-press state


def test_top_row_selectors_switch_profiles():
    app = make_app()
    assert app.router.active == ProfileId.DECKS
    press(app, P.CC_USER1, top=True, t=0)
    assert app.router.active == ProfileId.MIXER_FX
    press(app, P.CC_USER2, top=True, t=10)
    assert app.router.active == ProfileId.DECKS


def test_fader_uses_green_inc_red_dec_d01():
    fx = PROFILES[ProfileId.MIXER_FX]
    f = [b for b in fx.bindings if b.control_id == "mixer.ch1"]
    assert {b.color for b in f} == {"red", "green"}
    assert {b.role for b in f} == {"dec", "inc"}
