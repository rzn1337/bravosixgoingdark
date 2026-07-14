from __future__ import annotations

from ..humanize import random_point, screen_rect
from .base import Activity, close_app, focus_window

# Benign, read-only commands — harmless even if a keystroke leaks to another window.
_POSIX_CMDS = [
    "ls",
    "ls -la",
    "pwd",
    "whoami",
    "date",
    "echo hello",
    "echo working...",
    "uptime",
    "df -h",
    "free -h",
    "uname -a",
    "hostname",
    "id",
    "cal",
    "echo $HOME",
    "ls ~",
]
_WINDOWS_CMDS = [
    "dir",
    "echo hello",
    "whoami",
    "date /t",
    "time /t",
    "ver",
    "hostname",
    "cd",
    "echo %USERNAME%",
    "vol",
]


class TerminalWork(Activity):
    """Open a NEW terminal, type and run a few benign, read-only commands
    (ls, echo, date, ...) with the odd safe-region click mixed in, then close the
    terminal. A fresh terminal is opened each time this runs — distinct from the
    Notepad-style ``write`` activity."""

    name = "terminal"

    def run(self) -> None:
        ctx = self.ctx
        rng = ctx.rng
        cfg = ctx.settings.terminal

        ctx.log.info(
            "terminal: opening a new terminal (%s)", ctx.apps.terminal or "default"
        )
        proc = ctx.apps.launch_terminal()
        if proc is not None:
            ctx.tracked.append(proc)

        if not ctx.exe.wait(rng.uniform(2.0, 3.5)):  # let it come up
            return
        ctx.focus.activate(ctx.apps.terminal_title_hints())
        focus_window(ctx)
        if not ctx.exe.wait(rng.uniform(0.4, 0.9)):
            close_app(ctx, proc, ctrl_w=False)
            return

        pool = (
            list(cfg.commands)
            if cfg.commands
            else (_WINDOWS_CMDS if ctx.info.is_windows else _POSIX_CMDS)
        )
        k = min(rng.randint(cfg.min_cmds, cfg.max_cmds), len(pool))
        cmds = rng.sample(pool, k) if k > 0 else []
        margin = getattr(ctx.settings, "click_safe_margin", 0.15)
        rect = screen_rect(ctx.screen_size, margin=margin)

        for cmd in cmds:
            if ctx.control.stopped():
                break
            # a safe-region click mixed in ("write and click together")
            if rng.random() < 0.6:
                x, y = random_point(rect, rng)
                ctx.log.info("terminal: click (%d, %d)", x, y)
                ctx.exe.move_click(x, y)
                ctx.exe.wait(rng.uniform(0.3, 1.0))
            focus_window(ctx)  # ensure the terminal has focus before typing
            ctx.exe.wait(rng.uniform(0.3, 0.6))
            ctx.log.info("terminal: run `%s`", cmd)
            ctx.exe.type_text(cmd)
            ctx.exe.hotkey("enter")
            if not ctx.exe.wait(rng.uniform(1.5, 4.0)):
                break

        # close the terminal (exit the shell), then reap the process as a backstop
        ctx.log.info("terminal: closing")
        ctx.exe.type_text("exit")
        ctx.exe.hotkey("enter")
        ctx.exe.wait(rng.uniform(0.8, 1.6))
        close_app(ctx, proc, ctrl_w=False)
