import datetime as dt

import pytz


def get_time_now(*, offset=0):
    return dt.datetime.now(pytz.timezone("Australia/Perth")) + dt.timedelta(hours=offset)


def get_date(offset=0):
    date = get_time_now() + dt.timedelta(days=offset)
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    return date
