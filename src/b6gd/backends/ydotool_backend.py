from __future__ import annotations

import subprocess

from ..platform_detect import PlatformInfo
from ..screen import get_screen_size
from ..util.logging import get_logger
from .base import InputBackend

# Linux input-event key codes (from linux/input-event-codes.h).
_YKEYS = {
    "esc": 1,
    "escape": 1,
    "backspace": 14,
    "tab": 15,
    "enter": 28,
    "return": 28,
    "ctrl": 29,
    "control": 29,
    "s": 31,
    "leftshift": 42,
    "shift": 42,
    "alt": 56,
    "space": 57,
    "up": 103,
    "left": 105,
    "right": 106,
    "down": 108,
    "home": 102,
    "end": 107,
    "pageup": 104,
    "pagedown": 109,
    "delete": 111,
    "super": 125,
    "win": 125,
    "cmd": 125,
}

# click bitmask: 0x40 = down, 0x80 = up; low bits select the button.
_YBUTTON = {"left": 0x00, "right": 0x01, "middle": 0x02}


class YdotoolBackend(InputBackend):
    """Experimental Wayland backend that shells out to ``ydotool`` (which
    injects at the kernel uinput level). Requires ``ydotoold`` running and the
    right permissions — see the README. Best-effort: unsupported operations
    warn rather than crash. The pynput backend (Windows / X11) is the primary,
    fully supported path."""

    name = "ydotool"

    def __init__(self, info: PlatformInfo) -> None:
        self._info = info
        self._log = get_logger()
        self._pos = (0, 0)
        self._size = get_screen_size(info)
        self._warned = set()

    def _run(self, args) -> None:
        try:
            subprocess.run(
                ["ydotool", *[str(a) for a in args]],
                capture_output=True,
                timeout=5,
                check=False,
            )
        except Exception as exc:  # pragma: no cover - env dependent
            key = args[0] if args else "?"
            if key not in self._warned:
                self._log.warning("ydotool %s failed: %s", key, exc)
                self._warned.add(key)

    def move(self, x: int, y: int) -> None:
        self._pos = (int(x), int(y))
        self._run(["mousemove", "--absolute", "-x", int(x), "-y", int(y)])

    def position(self) -> tuple[int, int]:
        return self._pos

    def _click_code(self, button: str, down: bool, up: bool) -> int:
        code = _YBUTTON.get(button, 0x00)
        if down:
            code |= 0x40
        if up:
            code |= 0x80
        return code

    def mouse_down(self, button: str = "left") -> None:
        self._run(["click", hex(self._click_code(button, True, False))])

    def mouse_up(self, button: str = "left") -> None:
        self._run(["click", hex(self._click_code(button, False, True))])

    def click(self, button: str = "left") -> None:
        self._run(["click", hex(self._click_code(button, True, True))])

    def scroll(self, dy: int) -> None:
        self._run(["mousemove", "--wheel", "-x", 0, "-y", int(dy)])

    def _code(self, key: str):
        return _YKEYS.get(key.lower())

    def key_tap(self, key: str) -> None:
        code = self._code(key)
        if code is None:
            if key not in self._warned:
                self._log.warning("ydotool: unmapped key %r", key)
                self._warned.add(key)
            return
        self._run(["key", f"{code}:1", f"{code}:0"])

    def type_char(self, ch: str) -> None:
        self._run(["type", "--key-delay", 0, "--", ch])

    def hotkey(self, *keys: str) -> None:
        codes = [self._code(k) for k in keys]
        if any(c is None for c in codes):
            self._log.warning("ydotool: unmapped hotkey %s", "+".join(keys))
            return
        seq = [f"{c}:1" for c in codes] + [f"{c}:0" for c in reversed(codes)]
        self._run(["key", *seq])

    def screen_size(self) -> tuple[int, int]:
        return self._size
