from __future__ import annotations

from ..platform_detect import PlatformInfo
from ..screen import get_screen_size
from .base import InputBackend


class PynputBackend(InputBackend):
    """Real input via pynput. Works on Windows (SendInput) and Linux/X11
    (python-xlib) and macOS (Quartz). pynput is imported lazily so the rest of
    the app has no hard dependency on it."""

    name = "pynput"

    def __init__(self, info: PlatformInfo) -> None:
        from pynput.keyboard import Controller as KeyController
        from pynput.keyboard import Key
        from pynput.mouse import Button
        from pynput.mouse import Controller as MouseController

        self._info = info
        self._mouse = MouseController()
        self._kbd = KeyController()
        self._size = get_screen_size(info)

        self._buttons = {
            "left": Button.left,
            "right": Button.right,
            "middle": Button.middle,
        }
        self._keymap = {
            "enter": Key.enter,
            "return": Key.enter,
            "tab": Key.tab,
            "backspace": Key.backspace,
            "delete": Key.delete,
            "esc": Key.esc,
            "escape": Key.esc,
            "space": Key.space,
            "up": Key.up,
            "down": Key.down,
            "left": Key.left,
            "right": Key.right,
            "home": Key.home,
            "end": Key.end,
            "pageup": Key.page_up,
            "pagedown": Key.page_down,
            "ctrl": Key.ctrl,
            "control": Key.ctrl,
            "alt": Key.alt,
            "shift": Key.shift,
            "cmd": Key.cmd,
            "super": Key.cmd,
            "win": Key.cmd,
        }

    def _resolve(self, key: str):
        return self._keymap.get(key.lower(), key)

    def move(self, x: int, y: int) -> None:
        self._mouse.position = (int(x), int(y))

    def position(self) -> tuple[int, int]:
        px, py = self._mouse.position
        return int(px), int(py)

    def mouse_down(self, button: str = "left") -> None:
        self._mouse.press(self._buttons[button])

    def mouse_up(self, button: str = "left") -> None:
        self._mouse.release(self._buttons[button])

    def scroll(self, dy: int) -> None:
        self._mouse.scroll(0, dy)

    def key_tap(self, key: str) -> None:
        k = self._resolve(key)
        self._kbd.press(k)
        self._kbd.release(k)

    def type_char(self, ch: str) -> None:
        self._kbd.type(ch)

    def hotkey(self, *keys: str) -> None:
        resolved = [self._resolve(k) for k in keys]
        for k in resolved:
            self._kbd.press(k)
        for k in reversed(resolved):
            self._kbd.release(k)

    def screen_size(self) -> tuple[int, int]:
        return self._size
