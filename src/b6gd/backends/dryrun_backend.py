from __future__ import annotations

from ..platform_detect import PlatformInfo
from ..screen import get_screen_size
from ..util.logging import get_logger
from .base import InputBackend


class DryRunBackend(InputBackend):
    """Executes nothing. Tracks a virtual cursor and logs primitives at DEBUG.
    Uses no third-party deps, so dry-run and unit tests work anywhere
    (including headless CI)."""

    name = "dryrun"

    def __init__(self, info: PlatformInfo) -> None:
        self._log = get_logger()
        self._pos = (0, 0)
        self._size = get_screen_size(info)

    def move(self, x: int, y: int) -> None:
        self._pos = (int(x), int(y))
        self._log.debug("[dry] move -> %s", self._pos)

    def position(self) -> tuple[int, int]:
        return self._pos

    def mouse_down(self, button: str = "left") -> None:
        self._log.debug("[dry] mouse_down %s @ %s", button, self._pos)

    def mouse_up(self, button: str = "left") -> None:
        self._log.debug("[dry] mouse_up %s", button)

    def scroll(self, dy: int) -> None:
        self._log.debug("[dry] scroll %+d", dy)

    def key_tap(self, key: str) -> None:
        self._log.debug("[dry] key %s", key)

    def type_char(self, ch: str) -> None:
        self._log.debug("[dry] type %r", ch)

    def hotkey(self, *keys: str) -> None:
        self._log.debug("[dry] hotkey %s", "+".join(keys))

    def screen_size(self) -> tuple[int, int]:
        return self._size
