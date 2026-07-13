from __future__ import annotations

from ..engine.context import Context


class Activity:
    name = "base"

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    def run(self) -> None:
        raise NotImplementedError


def focus_window(ctx) -> None:
    """Click near the centre of the screen to focus the app we just launched.
    On Wayland we can't raise a window programmatically, but click-to-focus works
    — and it keeps keystrokes/scrolls from leaking into the terminal."""
    w, h = ctx.screen_size
    ctx.exe.move_click(int(w * 0.5), int(h * 0.45))


def close_app(ctx, proc, ctrl_w: bool = True) -> None:
    """Close the window/tab of a launched app and reap its process, so long runs
    don't accumulate hundreds of windows (which exhausts file descriptors).

    ``ctrl_w`` sends Ctrl+W (clean close for browsers/file managers). For the
    text editor we skip it (unsaved docs would prompt) and just terminate."""
    if ctrl_w:
        try:
            ctx.exe.hotkey("ctrl", "w")
            ctx.exe.wait(0.5)
        except Exception:
            pass
    if proc is not None:
        try:
            if proc in ctx.tracked:
                ctx.tracked.remove(proc)
        except Exception:
            pass
        try:
            if proc.poll() is None:
                proc.terminate()
        except Exception:
            pass
