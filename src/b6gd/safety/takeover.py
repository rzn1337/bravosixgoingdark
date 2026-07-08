from __future__ import annotations

import threading
import time

from ..screen import get_screen_size
from .control import Control


class TakeoverGuard:
    """Watches real input and pauses automation the moment the human takes
    over, auto-resuming after a quiet cooldown. Also provides a corner-slam
    hard stop (move the mouse hard into the top-left corner).

    Distinguishing our injected events from the user's is inherently
    imperfect; this uses two heuristics: (1) ignore input while we're mid
    injection burst and for a short guard window after, and (2) while we ARE
    injecting, treat a large jump away from the cursor position we last
    commanded as a human grab. The kill-switch is the hard guarantee; this is
    convenience.
    """

    CORNER_PX = 2
    MOVE_DEVIATION_PX = 130
    INJECT_GUARD_S = 0.25

    def __init__(self, control: Control, cooldown_s: float, info, logger) -> None:
        self._control = control
        self._cooldown = cooldown_s
        self._info = info
        self._log = logger
        self._mouse_listener = None
        self._kbd_listener = None
        self._resume_thread = None
        self._human_last = 0.0
        self._paused_by_me = False

    def start(self) -> bool:
        try:
            from pynput import keyboard, mouse
        except Exception as exc:  # pragma: no cover - env dependent
            self._log.warning(
                "Takeover auto-pause unavailable (pynput import failed: %s).", exc
            )
            return False
        self._mouse_listener = mouse.Listener(
            on_move=self._on_move, on_click=self._on_click, on_scroll=self._on_scroll
        )
        self._kbd_listener = keyboard.Listener(on_press=self._on_key)
        self._mouse_listener.start()
        self._kbd_listener.start()
        self._resume_thread = threading.Thread(target=self._resume_loop, daemon=True)
        self._resume_thread.start()
        self._log.info(
            "Takeover auto-pause armed (resumes after %.0fs of no human input).",
            self._cooldown,
        )
        return True

    # ---- heuristics ---------------------------------------------------
    def _guarded(self) -> bool:
        """True while we should ignore input (our own burst / just after)."""
        c = self._control
        return c.injecting or (time.monotonic() - c.last_injection) < self.INJECT_GUARD_S

    def _trigger(self) -> None:
        self._human_last = time.monotonic()
        if not self._control.is_paused():
            self._log.info("Human input detected — pausing automation.")
        self._control.pause()
        self._paused_by_me = True

    # ---- listeners ----------------------------------------------------
    def _on_move(self, x, y):
        if x <= self.CORNER_PX and y <= self.CORNER_PX:
            self._log.warning("Mouse slammed to top-left corner — KILL-SWITCH.")
            self._control.stop()
            return False  # stop this listener
        c = self._control
        if c.injecting:
            ex, ey = c.expected_pos
            if abs(x - ex) + abs(y - ey) > self.MOVE_DEVIATION_PX:
                self._trigger()
            return None
        if (time.monotonic() - c.last_injection) < self.INJECT_GUARD_S:
            return None
        self._trigger()
        return None

    def _on_click(self, x, y, button, pressed):
        if pressed and not self._guarded():
            self._trigger()

    def _on_scroll(self, x, y, dx, dy):
        if not self._guarded():
            self._trigger()

    def _on_key(self, key):
        if not self._guarded():
            self._trigger()

    def _resume_loop(self):
        while not self._control.stopped():
            if (
                self._paused_by_me
                and self._control.is_paused()
                and (time.monotonic() - self._human_last) >= self._cooldown
            ):
                self._log.info("No human input for %.0fs — resuming.", self._cooldown)
                self._control.resume()
                self._paused_by_me = False
            time.sleep(0.2)

    def stop(self):
        for listener in (self._mouse_listener, self._kbd_listener):
            try:
                if listener is not None:
                    listener.stop()
            except Exception:
                pass
        self._mouse_listener = None
        self._kbd_listener = None
