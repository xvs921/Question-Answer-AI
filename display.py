import datetime


def format_date(value):
    if isinstance(value, datetime.datetime):
        # pymongo returns naive datetimes that are in UTC
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.timezone.utc)
        return value.astimezone().strftime("%Y-%m-%d %H:%M")
    # Old records store the date as a string
    return "" if value is None else str(value)


def shorten(text, width):
    text = " ".join(str(text).split())
    return text if len(text) <= width else text[:width - 1] + "…"
