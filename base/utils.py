import calendar
import datetime
import decimal
import re
from django.core.serializers.json import DjangoJSONEncoder
from typing import Iterator, Optional

from base import constants


class KgDate:
    """
    A date class that is more ergonomic to use than ``datetime.date``.
    """

    def __init__(self, *, year: int, month: int, day: Optional[int] = None) -> None:
        self.year = year
        self.month = month
        self.day = day

    def replace(
        self,
        *,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ) -> "KgDate":
        if year is None:
            year = self.year

        if month is None:
            month = self.month

        if day is None:
            day = self.day

        return KgDate(year=year, month=month, day=day)

    def plus(self, *, years: int = 0, months: int = 0, days: int = 0) -> "KgDate":
        if years != 0:
            if months != 0 or days != 0:
                raise ValueError

            return KgDate(year=self.year + years, month=self.month, day=self.day)

        if months != 0:
            if days != 0:
                raise ValueError

            year_increment, month = divmod(self.month + months, 12)
            return KgDate(year=self.year + year_increment, month=month, day=self.day)

        if days != 0:
            if days >= 28:
                raise ValueError

            if self.day is None:
                raise ValueError

            days_in_month = get_days_in_month(self.year, self.month)
            if self.day + days > days_in_month:
                new_day = (self.day + days) - days_in_month
                if self.month == 12:
                    return KgDate(year=self.year + 1, month=1, day=new_day)
                else:
                    return KgDate(year=self.year, month=self.month + 1, day=new_day)
            else:
                return KgDate(year=self.year, month=self.month, day=self.day + days)

        return self

    def minus(self, *, years: int = 0, months: int = 0, days: int = 0) -> "KgDate":
        if years != 0:
            if months != 0 or days != 0:
                raise ValueError

            return KgDate(year=self.year - years, month=self.month, day=self.day)

        if months != 0:
            if days != 0:
                raise ValueError

            # We have to subtract 1 from `months` and then add it back again so that
            # the modular arithmetic works.
            year_increment, month = divmod(self.month - months - 1, 12)
            return KgDate(
                year=self.year + year_increment, month=month + 1, day=self.day
            )

        if days != 0:
            if days >= 28:
                raise ValueError

            if self.day is None:
                raise ValueError

            if self.day - days < 1:
                days_in_previous_month = (
                    get_days_in_month(self.year - 1, 1)
                    if self.month == 1
                    else get_days_in_month(self.year, self.month - 1)
                )
                new_day = days_in_previous_month + (self.day - days)
                if self.month == 1:
                    return KgDate(year=self.year - 1, month=12, day=new_day)
                else:
                    return KgDate(year=self.year, month=self.month - 1, day=new_day)
            else:
                return KgDate(year=self.year, month=self.month, day=self.day - days)

        return self

    def isoformat(self) -> str:
        if self.day is not None:
            return f"{self.year}-{self.month:0>2}-{self.day:0>2}"
        else:
            return f"{self.year}-{self.month:0>2}"

    def as_sql_pattern(self) -> str:
        if self.day is not None:
            return self.isoformat()
        else:
            return self.isoformat() + "%"

    def __eq__(self, other) -> bool:
        if isinstance(other, datetime.date):
            return (
                self.year == other.year
                and self.month == other.month
                and (self.day is None or self.day == other.day)
            )
        elif isinstance(other, KgDate):
            return (
                self.year == other.year
                and self.month == other.month
                and self.day == other.day
            )
        else:
            return NotImplemented

    def __repr__(self) -> str:
        if self.day is not None:
            return f"KgDate(year={self.year}, month={self.month}, day={self.day})"
        else:
            return f"KgDate(year={self.year}, month={self.month})"

    def __str__(self) -> str:
        return self.isoformat()


def time_to_minutes(t: datetime.time, *, normalize_pm: bool = False) -> int:
    """
    Returns the number of minutes since midnight for the ``datetime.time`` object.

    :param normalize_pm: If true, then morning times are treated as happening after
        afternoon and evening times instead of before.
    """
    return t.hour * 60 + t.minute + (24 * 60 if normalize_pm and t.hour < 12 else 0)


def within_range(
    month: datetime.date, start: datetime.date, end: datetime.date
) -> bool:
    """
    Returns true if any day of the range ``start`` to ``end`` is in the given month.

    The ``day`` field of ``month`` is ignored.
    """
    month_start = datetime.date(month.year, month.month, 1)
    ndays = get_days_in_month(month.year, month.month)
    month_end = datetime.date(month.year, month.month, ndays)
    return 0 < count_days_of_overlap(month_start, month_end, start, end)


def get_days_in_month(year: int, month: int) -> int:
    """
    Returns the number of days in the month.
    """
    return calendar.monthrange(year, month)[1]


def count_days_of_overlap(
    start1: datetime.date,
    end1: Optional[datetime.date],
    start2: datetime.date,
    end2: Optional[datetime.date],
):
    """
    Returns the number of days that fall between both ranges.

    One range or the other may be open-ended (with an `end` of None), but not both.

    The endpoints are included in the count of days.
    """
    assert end1 is None or start1 <= end1
    assert end2 is None or start2 <= end2
    assert not (end1 is None and end2 is None)

    start = max(start1, start2)
    end = min(end1, end2) if end1 and end2 else end1 or end2
    assert isinstance(end, datetime.date)
    return (end - start).days + 1 if start <= end else 0


def get_today_adjusted() -> datetime.date:
    """
    Returns the current date, adjusted so that early morning times count as the previous
    day.

    In most cases this should be used in preference to ``datetime.date.today()``.
    """
    now = datetime.datetime.now()
    if now.hour < 5:
        return now.date() - datetime.timedelta(days=1)
    else:
        return now.date()


date_pattern = re.compile(r"^([0-9]{4})-([0-9]{2})(-([0-9]{2}))?$")
time_pattern = re.compile(r"^([0-9]{1,2}):([0-9]{2})(:([0-9]{2}))?$")


def parse_date(s: str) -> datetime.date:
    """
    Parses a date in ``YYYY-MM-DD`` format into a ``datetime.date`` object.

    The day is optional and defaults to 1 if not specified.

    Raises ``ValueError`` if the date is not correctly formatted.
    """
    # Based on https://github.com/django/django/blob/master/django/utils/dateparse.py
    m = date_pattern.match(s)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(4)) if m.group(4) else 1
        return datetime.date(year=year, month=month, day=day)
    else:
        raise ValueError(s)


def parse_time(s: str) -> datetime.time:
    """
    Parses a time in ``HH:MM:SS`` into a ``datetime.time`` object.

    The second is optional and defaults to 0 if not specified. The leading digit of the
    hours may be omitted if it is '0'.

    Raises ``ValueError`` if the time is not correctly formatted.
    """
    # Based on https://github.com/django/django/blob/master/django/utils/dateparse.py
    m = time_pattern.match(s)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2))
        second = int(m.group(4)) if m.group(4) else 0
        return datetime.time(hour=hour, minute=minute, second=second)
    else:
        raise ValueError(s)


def format_time(t: datetime.time) -> str:
    """
    Returns the conventional human representation of  a ``datetime.time`` object.
    """
    # The hex code A0 is for the non-breaking space.
    return t.strftime("%I:%M\xa0%p").lstrip("0")


def remove_prefix(string: str, prefix: str) -> str:
    """
    If ``string`` begins with ``prefix``, returns ``string`` with ``prefix`` removed;
    otherwise returns ``string`` unchanged.
    """
    return string[len(prefix) :] if string.startswith(prefix) else string


def remove_suffix(string: str, suffix: str) -> str:
    """
    If ``string`` ends with ``suffix``, returns ``string`` with ``suffix`` removed;
    otherwise returns ``string`` unchanged.
    """
    return string[: -len(suffix)] if string.endswith(suffix) else string


def get_short_file_path(path: str) -> str:
    """
    Returns the short version of a file path, or the file path unchanged if it is not
    in ``constants.FILES``.
    """
    return remove_prefix(path, constants.FILES + "/")


def snake_case(s: str) -> str:
    """
    Converts an identifier from camel case to snake case.
    """

    def snake_case_replacer(match):
        text = match.group(0)
        return text[0] + "_" + text[1]

    name = re.sub(r"[a-z][A-Z]", snake_case_replacer, s)
    return name.lower()


def date_range(start: datetime.date, end: datetime.date) -> Iterator[datetime.date]:
    """
    Yields successive dates in the inclusive range from ``start`` to ``end``.
    """
    it = start
    while it <= end:
        yield it
        it += datetime.timedelta(days=1)


MONTHS_TO_INDICES = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)

        return super().default(o)
