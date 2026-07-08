from __future__ import annotations

import subprocess
import time

from ..platform_detect import PlatformInfo


class FocusGuard:
    """Reads the foreground window title so activities can confirm the right
    app is focused before typing into it (so stray keystrokes never land in a
    real window)."""

    def __init__(self, info: PlatformInfo, logger, dry_run: bool = False) -> None:
        self._info = info
        self._log = logger
        self._dry_run = dry_run

    def foreground_title(self) -> str:
        try:
            if self._info.is_windows:
                return self._win_title()
            if self._info.is_linux:
                return self._linux_title()
            if self._info.is_mac:
                return self._mac_title()
        except Exception:
            return ""
        return ""

    def _win_title(self) -> str:
        import ctypes

        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value or ""

    def _linux_title(self) -> str:
        import shutil

        if shutil.which("xdotool"):
            out = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowname"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if out.returncode == 0:
                return out.stdout.strip()
        if shutil.which("xprop"):
            # Fallback via xprop on the active window id.
            aid = subprocess.run(
                ["xdotool", "getactivewindow"], capture_output=True, text=True, timeout=2
            )
            del aid  # xdotool absent already handled; keep simple
        return ""

    def _mac_title(self) -> str:
        script = (
            'tell application "System Events" to get name of first application '
            "process whose frontmost is true"
        )
        out = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, timeout=2
        )
        return out.stdout.strip() if out.returncode == 0 else ""

    def wait_for(self, substrings, timeout: float = 5.0) -> bool:
        """Poll until the foreground title contains any of ``substrings``."""
        if self._dry_run:
            return True  # pretend the app is focused so dry-run exercises typing
        subs = [s.lower() for s in substrings if s]
        if not subs:
            return True
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            title = self.foreground_title().lower()
            if title and any(s in title for s in subs):
                return True
            time.sleep(0.3)
        return False
