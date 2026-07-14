from __future__ import annotations

from ..humanize import random_point, screen_rect
from .base import Activity, close_app

# Benign, read-only commands — harmless even if they somehow run elsewhere.
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


def _posix_script(cmds, rng) -> str:
    lines = []
    for c in cmds:
        safe = c.replace("'", "'\\''")
        lines.append("echo '+ %s'" % safe)  # show the command like a prompt
        lines.append(c)  # run it
        lines.append("sleep %d" % rng.randint(2, 4))
    lines.append("sleep %d" % rng.randint(2, 3))
    return "; ".join(lines)


def _windows_script(cmds, rng) -> str:
    lines = []
    for c in cmds:
        lines.append("echo + %s" % c)
        lines.append(c)
        lines.append("timeout /t %d >nul" % rng.randint(2, 4))
    lines.append("timeout /t 2 >nul")
    return " & ".join(lines)


class TerminalWork(Activity):
    """Open a NEW terminal that RUNS a few benign, read-only commands
    (ls, echo, date, ...) and closes itself when done — with the odd safe-region
    click alongside. A fresh terminal each time. Distinct from the Notepad-style
    ``write`` activity. Commands are run by the terminal (not typed), so it works
    even where we can't focus a window (Wayland)."""

    name = "terminal"

    def run(self) -> None:
        ctx = self.ctx
        rng = ctx.rng
        cfg = ctx.settings.terminal

        pool = (
            list(cfg.commands)
            if cfg.commands
            else (_WINDOWS_CMDS if ctx.info.is_windows else _POSIX_CMDS)
        )
        k = min(rng.randint(cfg.min_cmds, cfg.max_cmds), len(pool))
        cmds = rng.sample(pool, k) if k > 0 else ["echo hello"]

        ctx.log.info(
            "terminal: opening a terminal (%s) and running: %s",
            ctx.apps.terminal or "default",
            ", ".join(cmds),
        )
        proc = ctx.apps.launch_terminal_run(
            _posix_script(cmds, rng), _windows_script(cmds, rng)
        )
        if proc is not None:
            ctx.tracked.append(proc)

        # While the terminal runs its commands, do a few safe-region clicks.
        rect = screen_rect(
            ctx.screen_size, margin=getattr(ctx.settings, "click_safe_margin", 0.15)
        )
        for _ in range(rng.randint(2, 5)):
            if ctx.control.stopped():
                break
            x, y = random_point(rect, rng)
            ctx.log.info("terminal: safe click (%d, %d)", x, y)
            if not ctx.exe.move_click(x, y):
                break
            if not ctx.exe.wait(rng.uniform(1.0, 3.0)):
                break

        # Give the script a moment to finish; the terminal closes itself.
        ctx.exe.wait(rng.uniform(2.0, 4.0))
        close_app(ctx, proc, ctrl_w=False)  # backstop if it didn't auto-close
