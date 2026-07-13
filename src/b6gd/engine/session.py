from __future__ import annotations

import os
import random
import time

from .. import __version__
from ..activities import REGISTRY
from ..apps import Apps
from ..backends import make_backend
from ..content import ContentGen
from ..platform_detect import detect
from ..safety import (
    Control,
    FocusGuard,
    KillSwitch,
    Sandbox,
    StopFileWatcher,
    TakeoverGuard,
)
from ..util.duration import format_duration as fmt
from ..util.logging import get_logger
from .context import Context
from .executor import Executor
from .scheduler import Scheduler


class Session:
    """Owns the full run: builds the backend, safety guards, and activity
    context, then loops the scheduler for the configured duration."""

    def __init__(self, settings, dry_run: bool = False) -> None:
        self.settings = settings
        self.dry_run = dry_run
        self.log = get_logger()
        self.info = detect()
        self.rng = random.Random(settings.seed) if settings.seed else random.Random()
        self.control = Control()

        # May raise BackendUnavailable (e.g. Wayland without ydotool).
        self.backend = make_backend(self.info, dry_run=dry_run)

        self.sandbox = Sandbox(settings.sandbox_dir)
        self.sandbox.ensure()
        self.apps = Apps(self.info, settings, self.log, dry_run=dry_run)
        self.focus = FocusGuard(self.info, self.log, dry_run=dry_run)
        self.content = ContentGen(rng=self.rng)
        self.exe = Executor(self.backend, self.control, settings, self.log, self.rng)
        self.screen_size = self.backend.screen_size()

        self.ctx = Context(
            info=self.info,
            settings=settings,
            control=self.control,
            backend=self.backend,
            exe=self.exe,
            sandbox=self.sandbox,
            apps=self.apps,
            focus=self.focus,
            content=self.content,
            log=self.log,
            rng=self.rng,
            screen_size=self.screen_size,
            tracked=[],
        )

        self.available = [n for n in settings.activities if n in REGISTRY]
        self.scheduler = Scheduler(settings, self.available, self.rng)
        self.killswitch = KillSwitch(self.control, settings.killswitch, self.log)
        self.takeover = TakeoverGuard(
            self.control, settings.takeover_cooldown_s, self.info, self.log
        )
        self.stopfile = StopFileWatcher(
            self.control,
            os.path.join(os.path.expanduser("~"), ".b6gd_stop"),
            self.log,
        )

    def _banner(self, ks_armed: bool = False, tk_armed: bool = False) -> None:
        s = self.settings
        self.log.info("B6GD %s", __version__)
        self.log.info("  platform  : %s / %s", self.info.system, self.info.session_type)
        self.log.info(
            "  backend   : %s%s",
            self.backend.name,
            "  (DRY RUN - nothing is actually moved/typed)" if self.dry_run else "",
        )
        self.log.info("  duration  : %s", fmt(s.duration_s))
        self.log.info("  activities: %s", ", ".join(self.available))
        self.log.info("  screen    : %dx%d", self.screen_size[0], self.screen_size[1])
        self.log.info("  sandbox   : %s", self.sandbox.root)
        self.log.info(
            "  editor    : %s   files: %s",
            self.apps.editor or "(none)",
            self.apps.filemanager or "(none)",
        )
        if self.dry_run:
            self.log.info("  stop      : Ctrl+C (no global hotkey in dry-run)")
            return
        stops = []
        if ks_armed:
            stops.append(s.killswitch)
        if tk_armed:
            stops.append("slam mouse to top-left corner")
        stops.append("Ctrl+C")
        stops.append("touch %s" % self.stopfile.path)
        self.log.info("  stop      : %s", "  |  ".join(stops))
        if not ks_armed:
            self.log.warning(
                "  note      : global hotkey & auto-pause aren't available on this "
                "session; stop with Ctrl+C or `touch %s`.",
                self.stopfile.path,
            )

    def run(self) -> int:
        if not self.available:
            self.log.error(
                "No valid activities selected: %s (known: %s)",
                self.settings.activities,
                ", ".join(REGISTRY),
            )
            return 1

        ks_armed = tk_armed = False
        if not self.dry_run:
            ks_armed = self.killswitch.start()
            tk_armed = self.takeover.start()
            self.stopfile.start()
        self._banner(ks_armed, tk_armed)

        start = time.monotonic()
        end = start + self.settings.duration_s
        last = None
        count = 0
        sched = self.settings.schedule
        try:
            while not self.control.stopped() and time.monotonic() < end:
                name = self.scheduler.next_activity(last)
                if name is None:
                    break
                elapsed = time.monotonic() - start
                self.log.info(
                    ">> %s  [%s / %s]", name, fmt(elapsed), fmt(self.settings.duration_s)
                )
                try:
                    REGISTRY[name](self.ctx).run()
                except Exception as exc:  # one activity failing shouldn't kill the run
                    self.log.exception("activity %s error: %s", name, exc)
                last = name
                count += 1

                if self.control.stopped() or time.monotonic() >= end:
                    break
                if self.rng.random() < sched.break_chance:
                    pause = self.rng.uniform(sched.break_min_s, sched.break_max_s)
                    self.log.info("break: %s", fmt(pause))
                    if not self.control.wait(pause):
                        break
                else:
                    gap = self.rng.uniform(
                        sched.min_activity_gap_s, sched.max_activity_gap_s
                    )
                    if not self.control.wait(gap):
                        break
        except KeyboardInterrupt:
            self.log.info("Ctrl+C — stopping.")
        finally:
            self.control.stop()
            self._cleanup()
            self.log.info(
                "Session ended: %s elapsed, %d activities.",
                fmt(time.monotonic() - start),
                count,
            )
        return 0

    def _cleanup(self) -> None:
        try:
            if not self.dry_run:
                self.killswitch.stop()
                self.takeover.stop()
                self.stopfile.stop()
        except Exception:
            pass
        for proc in list(self.ctx.tracked):
            try:
                if proc is not None and proc.poll() is None:
                    proc.terminate()
            except Exception:
                pass
        try:
            self.ctx.tracked.clear()
        except Exception:
            pass
