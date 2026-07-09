from __future__ import annotations

import os
import threading
import time


class StopFileWatcher:
    """A dependency-free stop signal that works even where global hotkeys don't
    (e.g. Wayland, where pynput can't arm the kill-switch). Create the stop file
    from any terminal to halt the run:

        touch ~/.b6gd_stop
    """

    def __init__(self, control, path: str, logger) -> None:
        self._control = control
        self.path = path
        self._log = logger
        self._thread = None

    def start(self) -> bool:
        try:
            if os.path.exists(self.path):
                os.remove(self.path)  # clear a stale signal from a prior run
        except OSError:
            pass
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return True

    def _loop(self) -> None:
        while not self._control.stopped():
            if os.path.exists(self.path):
                self._log.warning("Stop file detected (%s) — stopping.", self.path)
                self._control.stop()
                break
            time.sleep(0.5)
        try:
            if os.path.exists(self.path):
                os.remove(self.path)
        except OSError:
            pass

    def stop(self) -> None:
        try:
            if os.path.exists(self.path):
                os.remove(self.path)
        except OSError:
            pass
