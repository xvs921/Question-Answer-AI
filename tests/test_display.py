import datetime

from display import format_date, shorten


def test_format_date_converts_utc_to_local_time():
    value = datetime.datetime(2026, 1, 5, 12, 30)  # naive UTC, as pymongo returns it
    expected = value.replace(tzinfo=datetime.timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    assert format_date(value) == expected


def test_format_date_keeps_old_string_dates():
    assert format_date("2026-1-5") == "2026-1-5"
    assert format_date(None) == ""


def test_shorten():
    assert shorten("short", 10) == "short"
    assert shorten("line one\nline two", 100) == "line one line two"
    assert shorten("a" * 20, 10) == "a" * 9 + "…"
