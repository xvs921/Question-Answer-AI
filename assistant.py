import logging

import wikipedia
import wolframalpha

import config
from database import find_all_which, find_cached_answer, insert_one_item

logger = logging.getLogger(__name__)


def ask_wolfram(question):
    if not config.WOLFRAM_APP_ID:
        logger.warning("WOLFRAM_APP_ID is not set, skipping WolframAlpha")
        return None
    try:
        res = wolframalpha.Client(config.WOLFRAM_APP_ID).query(question)
        first = next(iter(res.results), None)
    except Exception:
        logger.exception("WolframAlpha query failed")
        return None
    return first.text if first is not None else None


def ask_wikipedia(question):
    wikipedia.set_lang(config.WIKIPEDIA_LANG)
    try:
        return wikipedia.summary(question, sentences=3)
    except wikipedia.exceptions.PageError:
        logger.info("No Wikipedia page for %r", question)
    except wikipedia.exceptions.DisambiguationError as e:
        logger.info("Ambiguous Wikipedia query %r, options: %s", question, e.options[:5])
    except Exception:
        logger.exception("Wikipedia query failed")
    return None


def request_handle(question):
    """Answer the question and store the pair. Returns None if there is no answer."""
    try:
        cached = find_cached_answer(question)
    except Exception:
        logger.exception("Could not read cached answers from the database")
        cached = None
    if cached:
        logger.info("Answer for %r found in the database", question)
        return cached

    answer =ask_wolfram(question) or ask_wikipedia(question)
    if not answer:
        return None
    try:
        insert_one_item(question, answer)
    except Exception:
        # A failed save should not hide the answer from the user
        logger.exception("Could not save the answer to the database")
    return answer


def request_database(operation, text):
    if operation == "find":
        return find_all_which(text)
    raise ValueError(f"Unknown operation: {operation}")
