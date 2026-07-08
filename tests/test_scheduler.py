import random

from humansim.config import Settings
from humansim.engine.scheduler import Scheduler


def test_only_picks_available():
    s = Settings()
    sch = Scheduler(s, ["write", "idle"], random.Random(0))
    picks = {sch.next_activity(None) for _ in range(100)}
    assert picks <= {"write", "idle"}


def test_single_activity_returns_itself():
    sch = Scheduler(Settings(), ["idle"], random.Random(0))
    assert sch.next_activity("idle") == "idle"


def test_zero_repeat_penalty_never_repeats():
    s = Settings()
    s.schedule.repeat_penalty = 0.0
    sch = Scheduler(s, ["a", "b"], random.Random(0))
    last = "a"
    repeats = 0
    for _ in range(200):
        nxt = sch.next_activity(last)
        if nxt == last:
            repeats += 1
        last = nxt
    assert repeats == 0
