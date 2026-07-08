from __future__ import annotations

from .base import Activity


class SwitchWindows(Activity):
    """Alt-Tab between open windows with a natural dwell — ties the other
    activities together so the session doesn't feel like isolated bursts."""

    name = "switch"

    def run(self) -> None:
        ctx = self.ctx
        rng = ctx.rng
        for _ in range(rng.randint(1, 3)):
            if ctx.control.stopped():
                return
            ctx.log.info("switch: alt-tab")
            if not ctx.exe.hotkey("alt", "tab"):
                return
            if not ctx.exe.wait(rng.uniform(0.8, 2.5)):
                return
