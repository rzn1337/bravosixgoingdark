from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field, fields, is_dataclass


@dataclass
class MouseSettings:
    tremor_px: float = 1.2  # gaussian jitter along the path
    curvature: float = 0.18  # control-point deviation as a fraction of distance
    overshoot_chance: float = 0.2  # probability of overshoot-and-correct
    min_duration_s: float = 0.28  # move duration for very short hops
    max_duration_s: float = 1.4  # move duration for long traversals
    steps_per_100px: float = 14.0  # waypoint density


@dataclass
class TypingSettings:
    wpm: float = 55.0  # average words-per-minute
    wpm_jitter: float = 0.4  # per-keystroke gaussian jitter (fraction of base)
    typo_rate: float = 0.04  # probability a typo-eligible char is mistyped
    uncorrected_typo_fraction: float = 0.1  # fraction of typos left uncorrected
    think_pause_min_s: float = 0.4  # extra pause after sentence/line ends
    think_pause_max_s: float = 1.8


@dataclass
class ScheduleSettings:
    min_activity_gap_s: float = 0.5  # tiny gap between activities
    max_activity_gap_s: float = 3.0
    break_chance: float = 0.15  # chance of a longer break after an activity
    break_min_s: float = 5.0
    break_max_s: float = 25.0
    repeat_penalty: float = 0.35  # weight multiplier for repeating (weighted mode only)
    order: str = "shuffle"  # "shuffle" = equal frequency, random order; "weighted" = by weight


@dataclass
class WatchSettings:
    dwell_min_s: float = 45.0
    dwell_max_s: float = 150.0
    urls: list = field(
        default_factory=lambda: [
            "https://www.youtube.com/results?search_query=gohighlevel+automation+tutorial",
            "https://www.youtube.com/results?search_query=n8n+workflow+tutorial",
            "https://www.youtube.com/results?search_query=crm+automation+for+agencies",
            "https://www.youtube.com/results?search_query=gohighlevel+workflows+setup",
            "https://www.youtube.com/results?search_query=n8n+automation+examples",
        ]
    )


@dataclass
class Settings:
    duration_s: float = 1800.0
    activities: list = field(
        default_factory=lambda: ["write", "browse", "idle", "switch", "watch", "click"]
    )
    activity_weights: dict = field(
        default_factory=lambda: {
            "write": 3,
            "browse": 2,
            "idle": 2,
            "switch": 1,
            "watch": 2,
            "click": 2,
        }
    )
    sandbox_dir: str = ""  # empty => default ~/B6GDWorkspace
    killswitch: str = "<ctrl>+<alt>+q"
    takeover_cooldown_s: float = 6.0
    log_level: str = "INFO"
    logfile: str = ""
    editor_cmd: str = ""  # override editor auto-detection
    filemanager_cmd: str = ""  # override file-manager auto-detection
    assume_focus: bool = True  # type even when window focus can't be verified (e.g. Wayland)
    click_safe_margin: float = 0.15  # inset (fraction) for the random-click safe zone
    seed: int = 0  # 0 => nondeterministic
    mouse: MouseSettings = field(default_factory=MouseSettings)
    typing: TypingSettings = field(default_factory=TypingSettings)
    schedule: ScheduleSettings = field(default_factory=ScheduleSettings)
    watch: WatchSettings = field(default_factory=WatchSettings)


def default_sandbox() -> str:
    return os.path.join(os.path.expanduser("~"), "B6GDWorkspace")


def _merge(target, data: dict) -> None:
    valid = {f.name for f in fields(target)}
    for key, val in data.items():
        if key not in valid:
            continue
        cur = getattr(target, key)
        if is_dataclass(cur) and isinstance(val, dict):
            _merge(cur, val)
        else:
            setattr(target, key, val)


def load_settings(path: str | None = None) -> Settings:
    s = Settings()
    if path:
        # utf-8-sig tolerates a BOM (common on Windows-authored files).
        with open(path, "r", encoding="utf-8-sig") as fh:
            _merge(s, json.load(fh))
    if not s.sandbox_dir:
        s.sandbox_dir = default_sandbox()
    return s


def to_dict(s: Settings) -> dict:
    return asdict(s)
