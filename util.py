import datetime


def json_datetime_to_date(dt):
    dt = dt[:10]
    return datetime.date.fromisoformat(dt)


def is_in_range(json_dt, start_date, end_date):
    return start_date <= json_datetime_to_date(json_dt) <= end_date
