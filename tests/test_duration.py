import pytest

from humansim.util.duration import format_duration, parse_duration


def test_parse_units():
    assert parse_duration("30m") == 1800
    assert parse_duration("1h") == 3600
    assert parse_duration("90s") == 90
    assert parse_duration("45") == 45


def test_parse_combo():
    assert parse_duration("1h30m") == 5400
    assert parse_duration("2m30s") == 150


def test_parse_bad():
    with pytest.raises(ValueError):
        parse_duration("abc")


def test_format():
    assert format_duration(90) == "1m30s"
    assert format_duration(3600) == "1h"
    assert format_duration(0) == "0s"
