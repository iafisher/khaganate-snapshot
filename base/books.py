import datetime
from typing import List, Optional

from base.database import Database, Row
from base.utils import count_days_of_overlap, get_days_in_month, get_today_adjusted


def list_books(
    db: Database, year: Optional[int] = None, month: Optional[int] = None
) -> List[Row]:
    if month is not None:
        where = """
          date_started <= :end_of_month
          AND (
            date_ended IS NULL
            OR date_ended >= :start_of_month
          )
        """
        values = {
            "start_of_month": f"{year}-{month:0>2}-01",
            "end_of_month": f"{year}-{month:0>2}-31",
        }
        rows = db.select("book_entries", where=where, values=values)
    elif year is not None:
        where = """
          date_started <= :end_of_year
          AND (
            date_ended IS NULL
            OR date_ended >= :start_of_year
          )
        """
        values = {
            "start_of_year": f"{year}-01-01",
            "end_of_year": f"{year}-12-31",
        }
        rows = db.select("book_entries", where=where, values=values)
    else:
        rows = db.select("book_entries")

    # TODO(2021-10-01): Make this more efficient using a JOIN.
    return [_convert_entry(db, entry, year, month) for entry in rows]


def finish_book(db: Database, pk: int, payload: dict) -> Row:
    entry = db.get_by_pk("book_entries", pk)
    if entry["date_ended"] is not None:
        raise ValueError(f"book entry {pk} is already finished")

    pages = payload.pop("pages")
    if pages is not None:
        db.update_by_pk("books", entry["book"], {"pages": pages})

    db.update_by_pk("book_entries", pk, payload)
    entry = db.get_by_pk("book_entries", pk)
    return _convert_entry(db, entry)


def start_recommendation(db: Database, pk: int, payload: dict) -> Row:
    date = payload["date_started"]

    recommendation = db.get_by_pk("book_recommendations", pk)
    db.update_by_pk(
        "book_recommendations", recommendation["id"], {"date_removed": date}
    )

    entry = db.insert_and_get(
        "book_entries",
        {
            "book": recommendation["book"],
            "date_started": payload["date_started"],
            "date_ended": None,
            "abandoned": False,
            "skimmed": False,
            "rating": None,
        },
    )
    return _convert_entry(db, entry)


def start_book(db: Database, payload: dict) -> Row:
    date = get_today_adjusted()

    book_id = db.insert(
        "books",
        {
            "title": payload["title"],
            "authors": payload["authors"],
            "year": payload["year"],
            "edition": payload["edition"],
            "fictional": payload["fictional"],
            "pages": payload["pages"],
        },
    )

    entry = db.insert_and_get(
        "book_entries",
        {
            "book": book_id,
            "date_started": date,
            "date_ended": None,
            "abandoned": False,
            "skimmed": False,
        },
    )
    return _convert_entry(db, entry, date.year, date.month)


AVERAGE_PAGES = 300


def get_percentage_in_interval(
    entry: Row, year: Optional[int] = None, month: Optional[int] = None
) -> float:
    if entry["abandoned"] or not entry["date_ended"]:
        return 0.0

    if month is not None:
        assert year is not None
        start = datetime.date(year, month, 1)
        end = datetime.date(year, month, get_days_in_month(year, month))
    elif year is not None:
        start = datetime.date(year, 1, 1)
        end = datetime.date(year, 12, 31)
    else:
        return 1.0

    n = count_days_of_overlap(start, end, entry["date_started"], entry["date_ended"])
    return n / ((entry["date_ended"] - entry["date_started"]).days + 1)


def _convert_entry(
    db: Database, entry: Row, year: Optional[int] = None, month: Optional[int] = None
) -> Row:
    book = db.get_by_pk("books", entry["book"])
    converted_entry = {
        "book_id": book["id"],
        "entry_id": entry["id"],
        "title": book["title"],
        "authors": book["authors"],
        "date_started": entry["date_started"],
        "date_ended": entry["date_ended"],
        "abandoned": entry["abandoned"],
        "skimmed": entry["skimmed"],
        "fiction": book["fictional"],
        "pages": book["pages"],
        "rating": entry["rating"],
        "kg_link": book["kg_link"],
    }
    _set_value(converted_entry, year, month)
    return converted_entry


def _set_value(
    entry: Row, year: Optional[int] = None, month: Optional[int] = None
) -> None:
    entry["value"] = _get_value(entry)
    if year is not None:
        entry["percentage_in_interval"] = get_percentage_in_interval(entry, year, month)
        entry["value_in_interval"] = entry["value"] * entry["percentage_in_interval"]
    else:
        entry["percentage_in_interval"] = None
        entry["value_in_interval"] = None


def _get_value(entry: Row) -> float:
    v = entry["pages"] / AVERAGE_PAGES if entry["pages"] else 1
    if entry["skimmed"]:
        v *= 0.5
    return v
