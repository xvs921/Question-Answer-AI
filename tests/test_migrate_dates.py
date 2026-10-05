import datetime

import pytest

from migrate_dates import parse_old_date


def test_parse_old_date():
    assert parse_old_date("2026-1-5") == datetime.datetime(2026, 1, 5, tzinfo=datetime.timezone.utc)


def test_parse_old_date_rejects_garbage():
    with pytest.raises(ValueError):
        parse_old_date("yesterday")
