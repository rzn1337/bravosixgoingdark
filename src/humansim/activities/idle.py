from __future__ import annotations

from ..humanize import random_point, screen_rect
from .base import Activity


class IdleWander(Activity):
    """Drift the cursor around the screen with the occasional small scroll —
    the low-key 'thinking / reading' behaviour between busier activities."""

    name = "idle"

    def run(self) -> None:
        ctx = self.ctx
        rng = ctx.rng
        rect = screen_rect(ctx.screen_size)
        for _ in range(rng.randint(2, 5)):
            if ctx.control.stopped():
                return
            x, y = random_point(rect, rng)
            ctx.log.info("idle: drift to (%d, %d)", x, y)
            if not ctx.exe.move_to(x, y):
                return
            if rng.random() < 0.4:
                ctx.exe.scroll(rng.choice([-3, -2, 2, 3]))
            if not ctx.exe.wait(rng.uniform(0.5, 2.5)):
                return
