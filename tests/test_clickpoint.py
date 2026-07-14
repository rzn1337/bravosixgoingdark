import logging
import random

from b6gd.backends.dryrun_backend import DryRunBackend
from b6gd.config import Settings
from b6gd.engine.clickpoint import ClickPointRunner
from b6gd.engine.executor import Executor
from b6gd.platform_detect import detect
from b6gd.safety.control import Control


def test_click_at_moves_then_clicks():
    backend = DryRunBackend(detect())
    exe = Executor(backend, Control(), Settings(), logging.getLogger("t"), random.Random(0))
    assert exe.click_at(123, 456) is True
    assert backend.position() == (123, 456)


def test_click_point_runner_respects_count():
    runner = ClickPointRunner(
        Settings(), x=100, y=200, interval=0.0, count=3, dry_run=True
    )
    assert runner.run() == 0
