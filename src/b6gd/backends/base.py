from __future__ import annotations

from abc import ABC, abstractmethod


class InputBackend(ABC):
    """Atomic input primitives. All human-likeness lives ABOVE this layer;
    a backend just executes single, instantaneous actions."""

    name = "base"

    @abstractmethod
    def move(self, x: int, y: int) -> None:
        """Place the cursor at (x, y) immediately (no animation)."""

    @abstractmethod
    def position(self) -> tuple[int, int]:
        ...

    @abstractmethod
    def mouse_down(self, button: str = "left") -> None:
        ...

    @abstractmethod
    def mouse_up(self, button: str = "left") -> None:
        ...

    def click(self, button: str = "left") -> None:
        self.mouse_down(button)
        self.mouse_up(button)

    @abstractmethod
    def scroll(self, dy: int) -> None:
        """Scroll vertically by dy 'clicks' (positive = up)."""

    @abstractmethod
    def key_tap(self, key: str) -> None:
        """Press and release a single named key (e.g. 'enter', 'backspace')."""

    @abstractmethod
    def type_char(self, ch: str) -> None:
        """Type a single character."""

    @abstractmethod
    def hotkey(self, *keys: str) -> None:
        """Press keys together then release (e.g. hotkey('ctrl', 's'))."""

    @abstractmethod
    def screen_size(self) -> tuple[int, int]:
        ...

    def close(self) -> None:  # optional cleanup
        pass
