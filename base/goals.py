import datetime
from typing import Dict, List, Optional

from base.database import Database, Row
from base.exceptions import KhaganateImpossibleError
from base.metrics import METRICS_MAP


def list_current(db: Database, year: int, month: int) -> Dict[str, Row]:
    start_of_month = datetime.date(year=year, month=month, day=1)
    month_goals = db.select(
        "goals",
        where="timespan = 'month' AND date = :month",
        values={"month": start_of_month},
    )

    start_of_quarter = get_start_of_quarter(start_of_month)
    quarter_goals = db.select(
        "goals",
        where="timespan = 'quarter' AND date = :quarter",
        values={"quarter": start_of_quarter},
    )

    start_of_year = start_of_month.replace(month=1, day=1)
    year_goals = db.select(
        "goals",
        where="timespan = 'year' AND date = :year",
        values={"year": start_of_year},
    )

    _set_progress(db, start_of_month, month_goals)
    _set_progress(db, start_of_month, quarter_goals)
    _set_progress(db, start_of_month, year_goals)

    return {
        "month_goals": month_goals,
        "quarter_goals": quarter_goals,
        "year_goals": year_goals,
    }


def _set_progress(db: Database, today: datetime.date, goals: List[Row]) -> None:
    for goal in goals:
        auto_progress = get_auto_progress(db, today, goal)
        if auto_progress is None:
            # `auto_progress` tells the frontend not to allow the user to update the
            # progress manually.
            goal["auto_progress"] = False
        else:
            goal["auto_progress"] = True
            goal["progress"] = auto_progress


def get_auto_progress(db: Database, today: datetime.date, goal: Row) -> Optional[int]:
    """
    Calculates the progress for goals where progress can be calculated automatically.

    If progress cannot be calculated, then None is returned.
    """
    if goal["progress"] is not None:
        return None

    if goal["progress_from_task"] is not None:
        return _get_auto_progress_from_task(db, today, goal)

    if goal["progress_from_metric"]:
        return _get_auto_progress_from_metric(db, today, goal)

    return None


def _get_auto_progress_from_task(
    db: Database, today: datetime.date, goal: Row
) -> Optional[int]:
    # The goal's progress is set to the open/closed status of a task.
    task = db.get_by_pk("tasks", goal["progress_from_task"])
    return goal["max_progress"] if task["status"] == "fixed" else 0


def _get_auto_progress_from_metric(
    db: Database, today: datetime.date, goal: Row
) -> Optional[int]:
    # The goal's progress is set to the value of a metric.
    metric = goal["progress_from_metric"]
    function = METRICS_MAP[metric]["function"]
    if goal["timespan"] == "month":
        value = function(db, today.year, today.month)
    elif goal["timespan"] == "quarter":
        value = 0

        start_of_quarter = get_start_of_quarter(today)
        for delta in range(3):
            month = start_of_quarter.month + delta
            if month > today.month:
                break

            value += function(db, today.year, month)
    elif goal["timespan"] == "year":
        value = 0
        for month in range(1, 13):
            if month > today.month:
                break

            value += function(db, today.year, month)
    else:
        raise KhaganateImpossibleError(goal["timespan"])

    return value


def get_start_of_quarter(date: datetime.date) -> datetime.date:
    """
    Returns the date of the start of the quarter that the given date is in.
    """
    quarter = ((date.month - 1) // 3) + 1
    return date.replace(month=((quarter - 1) * 3) + 1, day=1)
