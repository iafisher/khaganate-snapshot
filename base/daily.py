"""
The implementation of the daily script invoked by `kgx daily`.
"""
import datetime

from base import goals as goals_service
from base.database import Database, Row
from base.utils import KgDate

MONDAY = 0
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6


def daily_task(db: Database, date: datetime.date) -> None:
    """
    Unconditionally runs the daily script.

    Unlike ``kgx daily``, this function DOES NOT check if the daily script has already
    been run. Callers of this function should generally do so themselves since running
    the daily script multiple times on the same day can cause redundant data in the
    database.
    """
    # On the first day of the month...
    if date.day == 1:
        # ...freeze the progress of auto-progress goals.
        freeze_auto_progress_goals(db, date)

    create_recurring_expenses(db, date)


def create_recurring_expenses(db: Database, date: datetime.date) -> None:
    # Create any recurring expenses, e.g.
    # if date.day == 1:
    #     db.insert(
    #         "credits",
    #         {
    #             "date_paid": date,
    #             "date_incurred": date,
    #             "amount": decimal.Decimal("10"),
    #             "vendor": get_vendor(db, "Spotify"),
    #             "category": get_credit_category(db, "Recreation", "Music"),
    #             "payment_method": "Discover",
    #         },
    #     )
    pass


def get_vendor(db: Database, name: str) -> Row:
    vendor = db.get("vendors", where="name = :name", values={"name": name})
    if vendor is None:
        raise Exception(f"no vendor named {name!r} found")
    return vendor["id"]


def get_credit_category(db: Database, category: str, subcategory: str) -> Row:
    category_row = db.get(
        "credit_categories",
        where="category = :category AND subcategory = :subcategory",
        values={"category": category, "subcategory": subcategory},
    )
    if category_row is None:
        raise Exception(f"category {category} / {subcategory} not found")
    return category_row["id"]


def freeze_auto_progress_goals(db: Database, date: datetime.date) -> None:
    last_day_of_timespan = date - datetime.timedelta(days=1)
    kg_date = KgDate(year=date.year, month=date.month, day=date.day)
    start_of_month = kg_date.minus(months=1)

    monthly_goals = db.select(
        "goals",
        where="timespan = 'month' AND date = :date",
        values={"date": start_of_month.isoformat()},
    )
    for goal in monthly_goals:
        auto_progress = goals_service.get_auto_progress(db, last_day_of_timespan, goal)
        if auto_progress is not None:
            db.update_by_pk("goals", goal["id"], {"progress": auto_progress})

    if ((date.month - 1) % 3) == 0:
        start_of_quarter = kg_date.minus(months=3)

        quarterly_goals = db.select(
            "goals",
            where="timespan = 'quarter' AND date = :date",
            values={"date": start_of_quarter.isoformat()},
        )
        for goal in quarterly_goals:
            auto_progress = goals_service.get_auto_progress(
                db, last_day_of_timespan, goal
            )
            if auto_progress is not None:
                db.update_by_pk("goals", goal["id"], {"progress": auto_progress})

    if date.month == 1:
        start_of_year = kg_date.minus(years=1)

        yearly_goals = db.select(
            "goals",
            where="timespan = 'year' AND date = :date",
            values={"date": start_of_year.isoformat()},
        )
        for goal in yearly_goals:
            auto_progress = goals_service.get_auto_progress(
                db, last_day_of_timespan, goal
            )
            if auto_progress is not None:
                db.update_by_pk("goals", goal["id"], {"progress": auto_progress})
