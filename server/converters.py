import datetime


class DateConverter:
    """
    A custom converter that allows the use of `<date:variable>` patterns in URL paths.

    https://docs.djangoproject.com/en/3.2/topics/http/urls/#registering-custom-path-converters
    """

    regex = "([0-9]{4})-([0-9]{2})-([0-9]{2})"

    def to_python(self, value: str) -> datetime.date:
        return datetime.date.fromisoformat(value)

    def to_url(self, value: datetime.date) -> str:
        return value.isoformat()
