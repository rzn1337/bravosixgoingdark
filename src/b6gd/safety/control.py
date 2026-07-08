from __future__ import annotations

import threading
import time


class Control:
    """Shared run-state: a hard stop plus a cooperative pause, and a small
    bit of bookkeeping so the takeover guard can tell our own injected input
    apart from the real user's.

    Every sleep in the app goes through :meth:`wait`, so a stop halts
    everything promptly and a pause freezes the countdown (rather than losing
    time) until resumed.
    """

    def __init__(self) -> None:
        self._stop = threading.Event()
        self._paused = threading.Event()  # set == currently paused
        self._lock = threading.Lock()
        self._inject_depth = 0
        self.last_injection = 0.0  # monotonic time we last emitted input
        self.expected_pos = (0, 0)  # where we last commanded the cursor

    # ---- stop ---------------------------------------------------------
    def stop(self) -> None:
        self._stop.set()
        self._paused.clear()  # unblock any pause wait so we can exit

    def stopped(self) -> bool:
        return self._stop.is_set()

    # ---- pause / resume ----------------------------------------------
    def pause(self) -> None:
        if not self._stop.is_set():
            self._paused.set()

    def resume(self) -> None:
        self._paused.clear()

    def is_paused(self) -> bool:
        return self._paused.is_set()

    # ---- injection bookkeeping ---------------------------------------
    def begin_injection(self) -> None:
        with self._lock:
            self._inject_depth += 1

    def end_injection(self) -> None:
        with self._lock:
            self._inject_depth = max(0, self._inject_depth - 1)
            self.last_injection = time.monotonic()

    @property
    def injecting(self) -> bool:
        return self._inject_depth > 0

    # ---- waiting ------------------------------------------------------
    def wait(self, seconds: float) -> bool:
        """Sleep for ``seconds`` of *active* time. Freezes while paused,
        returns False immediately if stopped, True when the time elapses."""
        deadline = time.monotonic() + max(0.0, seconds)
        while True:
            if self._stop.is_set():
                return False
            if self._paused.is_set():
                pstart = time.monotonic()
                while self._paused.is_set() and not self._stop.is_set():
                    time.sleep(0.05)
                if self._stop.is_set():
                    return False
                deadline += time.monotonic() - pstart
                continue
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return True
            time.sleep(min(remaining, 0.02))

    def check(self) -> bool:
        """Return False if stopped; block while paused. Called between
        primitives so activity halts the instant a pause/stop lands."""
        return self.wait(0.0)
