import datetime
import re
from unittest.mock import MagicMock

import pytest

import database


@pytest.fixture
def collection(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(database, "_collection", mock)
    return mock


def test_insert_stores_full_response_and_datetime(collection):
    long_answer = "x" * 500
    item_id = database.insert_one_item("question", long_answer)

    item = collection.insert_one.call_args.args[0]
    assert item["_id"] == item_id
    assert item["request"] == "question"
    assert item["response"] == long_answer
    assert isinstance(item["date"], datetime.datetime)


def test_find_escapes_regex_and_searches_both_fields(collection):
    collection.find.return_value.sort.return_value.limit.return_value = [{"_id": "1"}]

    result = database.find_all_which("a(b.c")

    query = collection.find.call_args.args[0]
    pattern = {"$regex": re.escape("a(b.c"), "$options": "i"}
    assert query == {"$or": [{"request": pattern}, {"response": pattern}]}
    assert result == [{"_id": "1"}]


def test_missing_connection_string_raises(monkeypatch):
    monkeypatch.setattr(database, "_collection", None)
    monkeypatch.setattr(database.config, "MONGO_URI", None)
    with pytest.raises(RuntimeError):
        database.get_collection()


def test_find_limits_results(collection):
    database.find_all_which("x", limit=5)
    collection.find.return_value.sort.return_value.limit.assert_called_once_with(5)


def test_cached_answer_returns_newest_response(collection):
    collection.find_one.return_value = {"response": "cached"}
    assert database.find_cached_answer("q") == "cached"
    assert collection.find_one.call_args.args[0] == {"request": "q"}


def test_cached_answer_none_when_missing(collection):
    collection.find_one.return_value = None
    assert database.find_cached_answer("q") is None


def test_indexes_created_on_connect(monkeypatch):
    collection = MagicMock()
    client = MagicMock()
    client.__getitem__.return_value.__getitem__.return_value = collection
    monkeypatch.setattr(database, "_collection", None)
    monkeypatch.setattr(database.config, "MONGO_URI", "mongodb://example")
    monkeypatch.setattr(database, "MongoClient", lambda *a, **kw: client)

    assert database.get_collection() is collection
    assert collection.create_index.call_count == 2
