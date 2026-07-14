from b6gd.activities import REGISTRY
from b6gd.cli import _parse_feature_selection, resolve_activities
from b6gd.config import Settings, TerminalSettings, WatchSettings

ALL = ["write", "browse", "idle", "switch", "watch", "click", "terminal"]


def test_interactive_typed_names_are_the_selection():
    # Typing names selects exactly those (not a toggle of the default).
    assert _parse_feature_selection("browse idle", ALL, ALL) == ["browse", "idle"]
    assert _parse_feature_selection("idle,browse", ALL, ALL) == ["browse", "idle"]


def test_interactive_empty_keeps_preselected():
    assert _parse_feature_selection("", ALL, ["write", "watch"]) == ["write", "watch"]


def test_interactive_ignores_unknown():
    assert _parse_feature_selection("browse bogus watch", ALL, ALL) == [
        "browse",
        "watch",
    ]


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
        "click",
        "terminal",
    ]


def test_terminal_feature_and_settings():
    s = Settings()
    assert "terminal" in s.activities
    assert "terminal" in REGISTRY
    t = TerminalSettings()
    assert t.min_cmds <= t.max_cmds


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
