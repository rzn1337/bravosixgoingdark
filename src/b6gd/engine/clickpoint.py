from __future__ import annotations

import os
import time

from .. import __version__
from ..backends import make_backend
from ..platform_detect import detect
from ..safety import Control, KillSwitch, StopFileWatcher
from ..util.duration import format_duration as fmt
from ..util.logging import get_logger
from .executor import Executor


class ClickPointRunner:
    """Repeatedly clicks a single fixed (x, y) point. A plain auto-clicker with
    the usual hard stops (kill-switch hotkey, stop-file, Ctrl+C)."""

    def __init__(
        self,
        settings,
        x,
        y,
        interval=1.0,
        count=0,
        duration=0.0,
        button="left",
        dry_run=False,
    ) -> None:
        self.settings = settings
        self.dry_run = dry_run
        self.log = get_logger()
        self.info = detect()
        self.control = Control()
        self.backend = make_backend(self.info, dry_run=dry_run)
        self.exe = Executor(self.backend, self.control, settings, self.log)
        self.x = int(x)
        self.y = int(y)
        self.interval = max(0.0, float(interval))
        self.count = max(0, int(count))
        self.duration = max(0.0, float(duration))
        self.button = button
        self.killswitch = KillSwitch(self.control, settings.killswitch, self.log)
        self.stopfile = StopFileWatcher(
            self.control, os.path.join(os.path.expanduser("~"), ".b6gd_stop"), self.log
        )

    def _banner(self, ks_armed: bool) -> None:
        self.log.info("B6GD %s - click-point", __version__)
        self.log.info("  platform  : %s / %s", self.info.system, self.info.session_type)
        self.log.info(
            "  backend   : %s%s",
            self.backend.name,
            "  (DRY RUN - not actually clicking)" if self.dry_run else "",
        )
        self.log.info("  point     : (%d, %d)   button=%s", self.x, self.y, self.button)
        self.log.info("  interval  : %gs", self.interval)
        if self.count:
            stop_after = "%d clicks" % self.count
        elif self.duration:
            stop_after = fmt(self.duration)
        else:
            stop_after = "never (until you stop it)"
        self.log.info("  stop after: %s", stop_after)
        w, h = self.backend.screen_size()
        if not (0 <= self.x < w and 0 <= self.y < h):
            self.log.warning("  note      : point is outside the %dx%d screen", w, h)
        if self.dry_run:
            self.log.info("  stop      : Ctrl+C")
        else:
            stops = []
            if ks_armed:
                stops.append(self.settings.killswitch)
            stops.append("Ctrl+C")
            stops.append("touch %s" % self.stopfile.path)
            self.log.info("  stop      : %s", "  |  ".join(stops))
            if not ks_armed:
                self.log.warning(
                    "  note      : global hotkey unavailable here; stop with Ctrl+C "
                    "or `touch %s`.",
                    self.stopfile.path,
                )

    def run(self) -> int:
        ks_armed = False
        if not self.dry_run:
            ks_armed = self.killswitch.start()
            self.stopfile.start()
        self._banner(ks_armed)

        clicked = 0
        start = time.monotonic()
        try:
            while not self.control.stopped():
                if self.count and clicked >= self.count:
                    break
                if self.duration and (time.monotonic() - start) >= self.duration:
                    break
                if not self.dry_run:
                    self.exe.click_at(self.x, self.y, self.button)
                clicked += 1
                if clicked <= 5 or clicked % 50 == 0:
                    self.log.info(
                        "%sclick %d at (%d, %d)",
                        "[dry] " if self.dry_run else "",
                        clicked,
                        self.x,
                        self.y,
                    )
                if not self.control.wait(self.interval):
                    break
        except KeyboardInterrupt:
            self.log.info("Ctrl+C - stopping.")
        finally:
            self.control.stop()
            if not self.dry_run:
                self.killswitch.stop()
                self.stopfile.stop()
            self.log.info(
                "Done: %d click(s) in %s.", clicked, fmt(time.monotonic() - start)
            )
        return 0
