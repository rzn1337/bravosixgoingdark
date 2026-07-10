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

    def can_detect(self) -> bool:
        """Whether we can actually read the foreground window title here. False
        on Wayland (xdotool is X11-only) or when no query tool is present."""
        if self._dry_run:
            return True
        if self._info.is_windows or self._info.is_mac:
            return True
        if self._info.is_linux and self._info.session_type == "x11":
            import shutil

            return shutil.which("xdotool") is not None
        return False

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

    def activate(self, title_hints) -> bool:
        """Best-effort: raise/focus a window whose title matches a hint. Works on
        Windows and X11; a no-op on Wayland/macOS (returns False)."""
        if self._dry_run:
            return True
        hints = [h.lower() for h in title_hints if h]
        if not hints:
            return False
        try:
            if self._info.is_windows:
                return self._activate_windows(hints)
            if self._info.is_linux and self._info.session_type == "x11":
                return self._activate_x11(hints)
        except Exception:
            return False
        return False

    def _activate_windows(self, hints) -> bool:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        found = []
        proto = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        def _cb(hwnd, _lparam):
            if not user32.IsWindowVisible(hwnd):
                return True
            n = user32.GetWindowTextLengthW(hwnd)
            if n == 0:
                return True
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            if any(h in buf.value.lower() for h in hints):
                found.append(hwnd)
                return False
            return True

        user32.EnumWindows(proto(_cb), 0)
        if not found:
            return False
        hwnd = found[0]
        user32.keybd_event(0x12, 0, 0, 0)  # ALT down helps bypass foreground lock
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
        user32.keybd_event(0x12, 0, 0x0002, 0)  # ALT up
        return True

    def _activate_x11(self, hints) -> bool:
        import shutil
        import subprocess

        for tool_args in (("wmctrl", "-a"), ("xdotool", "search", "--name")):
            if not shutil.which(tool_args[0]):
                continue
            for h in hints:
                cmd = list(tool_args) + [h]
                if tool_args[0] == "xdotool":
                    cmd += ["windowactivate"]
                try:
                    if subprocess.run(cmd, capture_output=True, timeout=2).returncode == 0:
                        return True
                except Exception:
                    pass
        return False

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
