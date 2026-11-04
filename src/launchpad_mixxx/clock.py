"""Injectable monotonic clock. Real loop uses time.monotonic_ms; tests use FakeClock."""
import time


class Clock:
    def now_ms(self) -> int:
        return int(time.monotonic() * 1000)


class FakeClock(Clock):
    def __init__(self, start_ms: int = 0):
        self.t = start_ms

    def now_ms(self) -> int:
        return self.t

    def advance(self, delta_ms: int) -> int:
        self.t += delta_ms
        return self.t
