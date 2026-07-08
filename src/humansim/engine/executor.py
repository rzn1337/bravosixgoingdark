from __future__ import annotations

import random

from ..humanize import plan_move, plan_typing


class Executor:
    """Drives the input backend with human-like motion and timing, routing
    every sleep through :class:`Control` so pause/stop take effect mid-action,
    and updating ``expected_pos`` so the takeover guard can track us."""

    def __init__(self, backend, control, settings, logger, rng=None) -> None:
        self.b = backend
        self.c = control
        self.s = settings
        self.log = logger
        self.rng = rng or random
        self.c.expected_pos = backend.position()

    def move_to(self, x: int, y: int) -> bool:
        start = self.b.position()
        plan = plan_move(start, (x, y), self.s.mouse, self.rng)
        self.c.begin_injection()
        try:
            for px, py, dt in plan:
                if not self.c.wait(dt):
                    return False
                self.b.move(px, py)
                self.c.expected_pos = (px, py)
        finally:
            self.c.end_injection()
        return not self.c.stopped()

    def click(self, button: str = "left") -> bool:
        if not self.c.check():
            return False
        self.c.begin_injection()
        try:
            self.b.click(button)
        finally:
            self.c.end_injection()
        return not self.c.stopped()

    def double_click(self, button: str = "left") -> bool:
        if not self.click(button):
            return False
        if not self.c.wait(self.rng.uniform(0.06, 0.12)):
            return False
        return self.click(button)

    def move_click(self, x: int, y: int, button: str = "left") -> bool:
        return self.move_to(x, y) and self.click(button)

    def scroll(self, clicks: int) -> bool:
        step = 1 if clicks > 0 else -1
        self.c.begin_injection()
        try:
            for _ in range(abs(int(clicks))):
                if not self.c.wait(self.rng.uniform(0.05, 0.16)):
                    return False
                self.b.scroll(step)
        finally:
            self.c.end_injection()
        return not self.c.stopped()

    def type_text(self, text: str) -> bool:
        events = plan_typing(text, self.s.typing, self.rng)
        self.c.begin_injection()
        try:
            for ev in events:
                if not self.c.wait(ev.delay):
                    return False
                if ev.kind == "char":
                    self.b.type_char(ev.value)
                else:
                    self.b.key_tap(ev.value)
        finally:
            self.c.end_injection()
        return not self.c.stopped()

    def hotkey(self, *keys: str) -> bool:
        if not self.c.check():
            return False
        self.c.begin_injection()
        try:
            self.b.hotkey(*keys)
        finally:
            self.c.end_injection()
        return not self.c.stopped()

    def wait(self, seconds: float) -> bool:
        return self.c.wait(seconds)
