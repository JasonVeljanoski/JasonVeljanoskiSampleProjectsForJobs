import datetime as dt

import pytz


def get_time_now(*, offset=0):
    return dt.datetime.now(pytz.timezone("Australia/Perth")) + dt.timedelta(hours=offset)


def get_date(offset=0):
    date = get_time_now() + dt.timedelta(days=offset)
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    return date


def format_date(value):
    """
    from: 1970-01-01 00:17:00+00:00
    to:   01/01/1970
    """
    if not isinstance(value, dt.datetime):
        value = None

    return value.strftime("%d/%m/%Y") if value else ""


def format_time(value):
    """
    from: 2022-02-01T12:30:00.000Z
    to:   12:30
    """
    if not isinstance(value, dt.datetime):
        value = None

    return value.strftime("%H:%M") if value else ""
