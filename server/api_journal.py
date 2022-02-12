import datetime
from django.http import HttpRequest, HttpResponse, JsonResponse

from base.database import Database
from base.utils import CustomJSONEncoder


def entries(request: HttpRequest, year: int, month: int) -> HttpResponse:
    with Database() as db:
        entries = db.select(
            "journal_entries",
            where="date LIKE :pattern",
            values={"pattern": f"{year}-{month:0>2}%"},
        )
        return JsonResponse(
            [{"date": e["date"], "entry": e["text"]} for e in entries], safe=False
        )


def entry(request: HttpRequest, year: int, month: int, day: int) -> HttpResponse:
    with Database() as db:
        date = datetime.date(year, month, day)
        book_entries = db.select(
            "book_entries",
            where=(
                "date_started <= :date AND "
                + "(date_ended >= :date OR date_ended IS NULL)"
            ),
            values={"date": date},
            get_related=True,
        )

        credits = db.select(
            "credits",
            where="date_incurred = :date",
            values={"date": date},
            get_related=True,
        )

        journal_entry = db.get(
            "journal_entries", where="date = :date", values={"date": date}
        )
        journal_entry = journal_entry["text"] if journal_entry else None

        payload = {
            "bookEntries": book_entries,
            "entry": journal_entry,
            "credits": credits,
        }
        return JsonResponse(payload, encoder=CustomJSONEncoder)
