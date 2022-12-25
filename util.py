import datetime


def json_datetime_to_date(dt):
    dt = dt[:10]
    return datetime.date.fromisoformat(dt)


def is_in_range(json_dt, start_date, end_date):
    return start_date <= json_datetime_to_date(json_dt) <= end_date


def get_months(start_date, end_date):
    (start_month, start_year) = (start_date.month, start_date.year)
    (end_month, end_year) = (end_date.month, end_date.year)

    if start_year > end_year:
        return []

    if start_year == end_year:
        return _get_months_of_one_year(start_year, start_month, end_month)

    # start_year < end_year.
    # Add the months of start_year
    res = _get_months_of_one_year(start_year, start_month, 12)

    # Add all the months of any middle years
    for year in range(start_year + 1, end_year):
        res += _get_months_of_one_year(year, 1, 12)

    # Add the months of end_year
    res += _get_months_of_one_year(end_year, 1, end_month)

    return res


def format_month_and_year(month, year):
    return f'{year}-{month:02d}'


def _get_months_of_one_year(year, start_month, end_month):
    return [format_month_and_year(m, year) for m in range(start_month, end_month + 1)]
