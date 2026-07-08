import random

from b6gd.config import TypingSettings
from b6gd.humanize.typing import plan_typing, planned_duration


def _chars(events):
    return "".join(e.value for e in events if e.kind == "char")


def test_no_typo_roundtrip():
    cfg = TypingSettings(typo_rate=0.0)
    ev = plan_typing("Hello world.", cfg, random.Random(0))
    assert _chars(ev) == "Hello world."
    assert all(e.delay >= 0 for e in ev)


def test_newline_becomes_enter():
    cfg = TypingSettings(typo_rate=0.0)
    ev = plan_typing("a\nb", cfg, random.Random(0))
    assert ("key", "enter") in [(e.kind, e.value) for e in ev]


def test_typos_are_corrected_with_backspace():
    cfg = TypingSettings(typo_rate=1.0, uncorrected_typo_fraction=0.0)
    ev = plan_typing("as", cfg, random.Random(3))
    assert any(e.kind == "key" and e.value == "backspace" for e in ev)


def test_duration_scales_inversely_with_wpm():
    slow = plan_typing(
        "a" * 100, TypingSettings(wpm=20, wpm_jitter=0.0, typo_rate=0.0), random.Random(0)
    )
    fast = plan_typing(
        "a" * 100, TypingSettings(wpm=120, wpm_jitter=0.0, typo_rate=0.0), random.Random(0)
    )
    assert planned_duration(slow) > planned_duration(fast)
