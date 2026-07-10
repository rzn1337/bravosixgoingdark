from b6gd.activities import REGISTRY
from b6gd.cli import resolve_activities
from b6gd.config import Settings, WatchSettings

ALL = ["write", "browse", "idle", "switch", "watch"]


def test_registry_has_all_including_watch():
    for name in ALL:
        assert name in REGISTRY


def test_resolve_default_is_all():
    assert resolve_activities(ALL, ALL, []) == ALL


def test_resolve_exclude_removes():
    assert resolve_activities(ALL, ALL, ["browse", "switch"]) == [
        "write",
        "idle",
        "watch",
    ]


def test_resolve_selected_then_exclude():
    assert resolve_activities(ALL, ["write", "browse", "watch"], ["browse"]) == [
        "write",
        "watch",
    ]


def test_resolve_drops_unknown_names():
    assert resolve_activities(ALL, ["write", "bogus"], []) == ["write"]


def test_defaults_include_watch_and_assume_focus():
    s = Settings()
    assert "watch" in s.activities
    assert s.assume_focus is True


def test_watch_settings_defaults_sane():
    w = WatchSettings()
    assert w.urls
    assert w.dwell_min_s < w.dwell_max_s
