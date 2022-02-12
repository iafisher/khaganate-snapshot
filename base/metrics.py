import datetime
import decimal
from typing import Any, Dict, List, Optional, Union, cast

from base import books as books_service
from base.database import Database


def get_metric(db: Database, metric_name: str) -> Optional[Dict[str, Any]]:
    metric: Optional[Dict[str, Any]] = None
    for m in METRICS:
        if m["name"] == metric_name:
            metric = m.copy()
            break

    if metric is None:
        return None

    values = []
    month = metric["start"]
    end = datetime.date.today() if metric["end"] is None else metric["end"]
    while month <= end:
        values.append(
            (month.isoformat(), metric["function"](db, month.year, month.month))
        )
        if month.month < 12:
            month = datetime.date(month.year, month.month + 1, 1)
        else:
            month = datetime.date(month.year + 1, 1, 1)

    del metric["function"]
    metric["values"] = values

    return metric


def list_metrics(db: Database, year: int, month: int) -> List[Dict[str, Any]]:
    month_object = datetime.date(year, month, 1)

    response = []
    for metric in cast(List[Dict[str, Any]], METRICS):
        if month_object < metric["start"]:
            continue

        if metric["end"] is not None and month_object >= metric["end"]:
            continue

        response.append(
            {
                "name": metric["name"],
                "displayTitle": metric["display_title"],
                "group": metric["group"],
                "type": metric["type"],
                "value": metric["function"](db, year, month),
                "good_threshold": metric["good_threshold"],
                "bad_threshold": metric["bad_threshold"],
                "higher_is_better": metric["higher_is_better"],
            }
        )

    return response


def D(
    n: Union[float, int], *, places: int, rounding=decimal.ROUND_DOWN
) -> decimal.Decimal:
    return decimal.Decimal(n).quantize(
        decimal.Decimal("." + ("0" * (places - 1)) + "1"), rounding=rounding
    )


def metric_bad_habits(db: Database, year: int, month: int) -> int:
    points = db.sql(
        """
        SELECT
          -SUM(points)
        FROM
          habit_entries
        WHERE
          strftime('%Y-%m', created_at, 'unixepoch') = :yearmonth
        AND
          points < 0
        """,
        values={"yearmonth": f"{year}-{month:0>2}"},
        multiple=False,
        as_tuple=True,
    )
    return points[0] or 0


def metric_good_habits(db: Database, year: int, month: int) -> int:
    points = db.sql(
        """
        SELECT
          SUM(points)
        FROM
          habit_entries
        WHERE
          strftime('%Y-%m', created_at, 'unixepoch') = :yearmonth
        AND
          points > 0
        """,
        values={"yearmonth": f"{year}-{month:0>2}"},
        multiple=False,
        as_tuple=True,
    )
    return points[0] or 0


def metric_net_income(db: Database, year: int, month: int) -> Optional[decimal.Decimal]:
    total_debited = db.sql(
        "SELECT SUM(amount) FROM debits WHERE date_incurred LIKE :pattern",
        {"pattern": f"{year}-{month:0>2}%"},
        multiple=False,
        as_tuple=True,
    )[0]

    if total_debited is None:
        return None

    total_credits = db.sql(
        "SELECT SUM(amount) FROM credits WHERE date_incurred LIKE :pattern",
        {"pattern": f"{year}-{month:0>2}%"},
        multiple=False,
        as_tuple=True,
    )[0]

    if total_credits is None:
        return None

    return D(total_debited - total_credits, places=2, rounding=decimal.ROUND_UP)


def metric_total_expenses(
    db: Database, year: int, month: int
) -> Optional[decimal.Decimal]:
    total = db.sql(
        "SELECT SUM(amount) FROM credits WHERE date_incurred LIKE :pattern",
        {"pattern": f"{year}-{month:0>2}%"},
        multiple=False,
        as_tuple=True,
    )[0]
    return D(total, places=2, rounding=decimal.ROUND_UP) if total is not None else None


def metric_books_read(db: Database, year: int, month: int) -> decimal.Decimal:
    books = books_service.list_books(db, year, month)
    return D(
        sum(book["value_in_interval"] for book in books),
        places=2,
    )


def metric_films_watched(db: Database, year: int, month: int) -> int:
    n = db.count(
        "film_entries",
        where="date_viewed LIKE :pattern",
        values={"pattern": f"{year}-{month:0>2}%"},
    )
    return n or 0


def metric_bookmarks_saved(db: Database, year: int, month: int) -> int:
    n = db.count(
        "bookmarks",
        where="strftime('%Y-%m', created_at, 'unixepoch') = :yearmonth",
        values={"yearmonth": f"{year}-{month:0>2}"},
    )
    return n or 0


def metric_journal_entries(db: Database, year: int, month: int) -> int:
    return db.count(
        "journal_entries",
        where="date LIKE :pattern",
        values={"pattern": f"{year}-{month:0>2}%"},
    )


def metric_journal_words(db: Database, year: int, month: int) -> int:
    entries = db.select(
        "journal_entries",
        where="date LIKE :pattern",
        values={"pattern": f"{year}-{month:0>2}%"},
    )
    return sum(len(entry["text"].split()) for entry in entries)


def metric_counties_visited(db: Database, year: int, month: int) -> int:
    return db.count(
        "county_visits",
        where=(
            "only_year = 0 AND date <= :month_end AND "
            + "(date_end >= :month_start OR date_end IS NULL)"
        ),
        values={
            "month_start": f"{year}-{month:0>2}-01",
            "month_end": f"{year}-{month:0>2}-31",
        },
        distinct="county",
    )


def metric_from_table(name: str):
    def f(db: Database, year: int, month: int) -> int:
        pattern = f"{year}-{month:0>2}%"
        row = db.get(
            "metrics",
            where="name = :name AND month LIKE :pattern",
            values={"name": name, "pattern": pattern},
        )
        return row["value"] if row is not None else None

    return f


def metric(
    name,
    *,
    display_title,
    function,
    type,
    start,
    end=None,
    suggested_min=None,
    suggested_max=None,
    group=None,
    good_threshold=None,
    bad_threshold=None,
    higher_is_better=True,
):
    return dict(
        name=name,
        display_title=display_title,
        function=function,
        type=type,
        start=start,
        end=end,
        suggested_min=suggested_min,
        suggested_max=suggested_max,
        group=group,
        good_threshold=good_threshold,
        bad_threshold=bad_threshold,
        higher_is_better=higher_is_better,
    )


METRICS = [
    metric(
        "bookmarks_saved",
        display_title="bookmarks saved",
        function=metric_bookmarks_saved,
        group="Productivity",
        type="integer",
        start=datetime.date(2018, 11, 1),
    ),
    metric(
        "books_read",
        display_title="books read",
        function=metric_books_read,
        group="Productivity",
        type="real",
        start=datetime.date(2014, 1, 1),
        good_threshold=3.0,
        bad_threshold=2.0,
    ),
    metric(
        "counties_visited",
        display_title="counties visited",
        function=metric_counties_visited,
        type="integer",
        start=datetime.date(2019, 9, 1),
    ),
    metric(
        "films_watched",
        display_title="films watched",
        function=metric_films_watched,
        group="Productivity",
        type="integer",
        start=datetime.date(2015, 3, 1),
        good_threshold=5,
        bad_threshold=1,
    ),
    metric(
        "habits_bad",
        display_title="bad habits score",
        function=metric_bad_habits,
        group="Personal",
        type="integer",
        start=datetime.date(2022, 1, 1),
    ),
    metric(
        "habits_good",
        display_title="good habits score",
        function=metric_good_habits,
        group="Personal",
        type="integer",
        start=datetime.date(2022, 1, 1),
    ),
    metric(
        "journal_entries",
        display_title="journal entries",
        function=metric_journal_entries,
        group="Personal",
        type="integer",
        start=datetime.date(2016, 11, 1),
    ),
    metric(
        "journal_words",
        display_title="journal words",
        function=metric_journal_words,
        group="Personal",
        type="integer",
        start=datetime.date(2016, 11, 1),
    ),
    metric(
        "net_income",
        display_title="net income",
        function=metric_net_income,
        group="Finances",
        type="dollar",
        start=datetime.date(2019, 7, 1),
    ),
    metric(
        "total_expenses",
        display_title="total expenses",
        function=metric_total_expenses,
        group="Finances",
        type="dollar",
        start=datetime.date(2019, 7, 1),
    ),
]

METRICS_MAP = {metric["name"]: metric for metric in METRICS}
