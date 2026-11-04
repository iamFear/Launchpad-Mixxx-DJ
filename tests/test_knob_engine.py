"""A04: knob repeat contract with fake clock (P01) — literal A04 numbers."""
from launchpad_mixxx.clock import FakeClock
from launchpad_mixxx.engine import ControlEngine


def test_knob_repeat_hits_contract_points():
    eng = ControlEngine({"gain": 0.0})
    c = FakeClock(0)
    eng.press_continuous("gain", +1, pad=1, now_ms=c.now_ms())
    assert eng.get_value("gain") == 0.0  # no immediate step; first tick steps
    c.advance(20)
    ticks = eng.tick(c.now_ms())
    assert eng.get_value("gain") == 1.0  # 1% at 20 ms
    assert ticks and ticks[0].value01 == 0.01
    c.advance(980)  # t = 1000 total
    eng.tick(c.now_ms())
    assert eng.get_value("gain") == 50.0, eng.get_value("gain")  # 50% at 1 s
    c.advance(1000)  # t = 2000 total
    eng.tick(c.now_ms())
    assert eng.get_value("gain") == 100.0  # 100% at 2 s
    c.advance(5000)  # hold past end: stays clamped
    eng.tick(c.now_ms())
    assert eng.get_value("gain") == 100.0


def test_release_cancels_future_ticks():
    eng = ControlEngine({"gain": 10.0})
    c = FakeClock(0)
    eng.press_continuous("gain", +1, pad=1, now_ms=0)
    c.advance(40)
    eng.tick(c.now_ms())
    assert eng.get_value("gain") == 12.0
    eng.release("gain", pad=1)
    c.advance(200)
    assert eng.tick(c.now_ms()) == []
    assert eng.get_value("gain") == 12.0


def test_symmetric_decrease_and_last_wins():
    eng = ControlEngine({"gain": 50.0})
    c = FakeClock(0)
    eng.press_continuous("gain", +1, pad=1, now_ms=0)
    eng.press_continuous("gain", -1, pad=2, now_ms=5)  # opposite: last wins
    c.advance(25)  # t=25: only the -1 hold (due at 25) fires
    eng.tick(c.now_ms())
    assert eng.get_value("gain") == 49.0


def test_tap_shorter_than_20ms_is_noop():
    eng = ControlEngine({"gain": 30.0})
    eng.press_continuous("gain", +1, pad=1, now_ms=100)
    eng.release("gain", pad=1)  # released after 5 ms, before first tick
    assert eng.get_value("gain") == 30.0
