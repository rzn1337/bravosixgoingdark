from __future__ import annotations

from ..humanize import random_point, screen_rect
from .base import Activity


class RandomClick(Activity):
    """Left-click a few random spots inside a safe central region of the screen —
    kept away from window controls, title/menu bars, the taskbar/dock, and the
    kill-switch corner. Single left-clicks only (no double-click, no right-click),
    so it won't open or trigger things at the edges."""

    name = "click"

    def run(self) -> None:
        ctx = self.ctx
        rng = ctx.rng
        margin = getattr(ctx.settings, "click_safe_margin", 0.15)
        rect = screen_rect(ctx.screen_size, margin=margin)
        for _ in range(rng.randint(2, 5)):
            if ctx.control.stopped():
                return
            x, y = random_point(rect, rng)
            ctx.log.info("click: safe click at (%d, %d)", x, y)
            if not ctx.exe.move_click(x, y):
                return
            if not ctx.exe.wait(rng.uniform(0.5, 2.5)):
                return
