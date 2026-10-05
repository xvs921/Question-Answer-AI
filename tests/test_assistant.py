import pytest
import wikipedia

import assistant


@pytest.fixture(autouse=True)
def no_cache(monkeypatch):
    monkeypatch.setattr(assistant, "find_cached_answer", lambda q: None)


@pytest.fixture
def saved(monkeypatch):
    calls = []
    monkeypatch.setattr(assistant, "insert_one_item", lambda q, a: calls.append((q, a)))
    return calls


def test_uses_wolfram_answer_first(monkeypatch, saved):
    monkeypatch.setattr(assistant, "ask_wolfram", lambda q: "42")
    monkeypatch.setattr(assistant, "ask_wikipedia", lambda q: pytest.fail("should not be called"))

    assert assistant.request_handle("q") == "42"
    assert saved == [("q", "42")]


def test_falls_back_to_wikipedia(monkeypatch, saved):
    monkeypatch.setattr(assistant, "ask_wolfram", lambda q: None)
    monkeypatch.setattr(assistant, "ask_wikipedia", lambda q: "wiki")

    assert assistant.request_handle("q") == "wiki"
    assert saved == [("q", "wiki")]


def test_no_answer_is_not_saved(monkeypatch, saved):
    monkeypatch.setattr(assistant, "ask_wolfram", lambda q: None)
    monkeypatch.setattr(assistant, "ask_wikipedia", lambda q: None)

    assert assistant.request_handle("q") is None
    assert saved == []


def test_answer_returned_even_if_save_fails(monkeypatch):
    def broken_save(q, a):
        raise ConnectionError("db down")

    monkeypatch.setattr(assistant, "insert_one_item", broken_save)
    monkeypatch.setattr(assistant, "ask_wolfram", lambda q: "42")

    assert assistant.request_handle("q") == "42"


def test_wolfram_skipped_without_app_id(monkeypatch):
    monkeypatch.setattr(assistant.config, "WOLFRAM_APP_ID", None)
    assert assistant.ask_wolfram("q") is None


def test_unknown_database_operation():
    with pytest.raises(ValueError):
        assistant.request_database("delete", "x")


def test_cached_answer_skips_apis_and_saving(monkeypatch, saved):
    monkeypatch.setattr(assistant, "find_cached_answer", lambda q: "from db")
    monkeypatch.setattr(assistant, "ask_wolfram", lambda q: pytest.fail("should not be called"))

    assert assistant.request_handle("q") == "from db"
    assert saved == []


def test_broken_cache_falls_back_to_apis(monkeypatch, saved):
    def broken_cache(q):
        raise ConnectionError("db down")

    monkeypatch.setattr(assistant, "find_cached_answer", broken_cache)
    monkeypatch.setattr(assistant, "ask_wolfram", lambda q: "42")

    assert assistant.request_handle("q") == "42"


@pytest.mark.parametrize("error", [
    wikipedia.exceptions.PageError("q"),
    wikipedia.exceptions.DisambiguationError("q", ["a", "b"]),
    ConnectionError("offline"),
])
def test_wikipedia_errors_return_none(monkeypatch, error):
    def raise_error(*args, **kwargs):
        raise error

    monkeypatch.setattr(assistant.wikipedia, "set_lang", lambda lang: None)
    monkeypatch.setattr(assistant.wikipedia, "summary", raise_error)
    assert assistant.ask_wikipedia("q") is None
