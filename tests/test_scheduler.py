import random

from b6gd.config import Settings
from b6gd.engine.scheduler import Scheduler


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
    s.schedule.order = "weighted"
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


def test_shuffle_equal_frequency():
    # Each activity runs exactly once per round -> equal frequency over N rounds.
    s = Settings()
    s.schedule.order = "shuffle"
    sch = Scheduler(s, ["a", "b", "c"], random.Random(0))
    counts = {"a": 0, "b": 0, "c": 0}
    last = None
    for _ in range(30):  # 10 full rounds of 3
        nxt = sch.next_activity(last)
        counts[nxt] += 1
        last = nxt
    assert counts == {"a": 10, "b": 10, "c": 10}


def test_shuffle_no_back_to_back_repeats():
    s = Settings()
    s.schedule.order = "shuffle"
    sch = Scheduler(s, ["a", "b", "c"], random.Random(1))
    last = None
    repeats = 0
    for _ in range(60):
        nxt = sch.next_activity(last)
        if nxt == last:
            repeats += 1
        last = nxt
    assert repeats == 0
