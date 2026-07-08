from __future__ import annotations

from .control import Control


class KillSwitch:
    """Global hotkey that hard-stops the session from anywhere.

    Default combo ``<ctrl>+<alt>+q`` (pynput hotkey syntax). Uses a lazy
    pynput import so dry-run / tests need no third-party deps.
    """

    def __init__(self, control: Control, combo: str, logger) -> None:
        self._control = control
        self._combo = combo
        self._log = logger
        self._hotkeys = None

    def start(self) -> bool:
        try:
            from pynput import keyboard
        except Exception as exc:  # pragma: no cover - env dependent
            self._log.error(
                "KILL-SWITCH UNAVAILABLE (pynput import failed: %s). "
                "Use Ctrl+C in the terminal, or slam the mouse to the top-left "
                "corner, to stop.",
                exc,
            )
            return False
        try:
            self._hotkeys = keyboard.GlobalHotKeys({self._combo: self._fire})
            self._hotkeys.start()
            self._log.info("Kill-switch armed: %s", self._combo)
            return True
        except Exception as exc:  # pragma: no cover - env dependent
            self._log.error("Could not arm kill-switch %r: %s", self._combo, exc)
            return False

    def _fire(self) -> None:
        self._log.warning("KILL-SWITCH pressed (%s) — stopping.", self._combo)
        self._control.stop()

    def stop(self) -> None:
        if self._hotkeys is not None:
            try:
                self._hotkeys.stop()
            except Exception:
                pass
            self._hotkeys = None
