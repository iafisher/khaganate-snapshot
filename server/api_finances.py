import decimal
import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.text import slugify
from typing import Callable

from base.database import Database, Row
from base.utils import CustomJSONEncoder, parse_date


def credits_create(request: HttpRequest) -> HttpResponse:
    with Database() as db:
        payload = json.loads(request.body, encoding="utf8")
        amount = decimal.Decimal(payload["amount"])
        payment_method = payload["paymentMethod"]
        date_paid = parse_date(payload["datePaid"])
        date_incurred = (
            parse_date(payload["dateIncurred"])
            if payload["dateIncurred"]
            else date_paid
        )
        vendor = payload["vendor"]
        category = payload["category"]
        notes = payload["notes"]

        if vendor:
            # The `newTag` field from Select2 flags whether the vendor is newly-created
            # or an existing database row.
            if vendor.get("newTag", False):
                vendor_id = db.insert("vendors", {"name": vendor["text"]})
            else:
                vendor_id = vendor["id"]
        else:
            vendor_id = None

        if category.get("newTag", False):
            parent_category, subcategory = category["text"].split("/")
            parent_category = parent_category.strip()
            subcategory = subcategory.strip()

            category_id = db.insert(
                "credit_categories",
                {
                    "category": parent_category,
                    "subcategory": subcategory,
                    "category_slug": slugify(parent_category),
                    "subcategory_slug": slugify(subcategory),
                },
            )
        else:
            category_id = category["id"]

        entry = db.insert_and_get(
            "credits",
            {
                "amount": amount,
                "payment_method": payment_method,
                "date_paid": date_paid,
                "date_incurred": date_incurred,
                "vendor": vendor_id,
                "category": category_id,
                "notes": notes,
            },
            get_related=True,
        )
        return JsonResponse(entry, encoder=CustomJSONEncoder)


def debits_create(request: HttpRequest) -> HttpResponse:
    with Database() as db:
        payload = json.loads(request.body, encoding="utf8")
        amount = decimal.Decimal(payload["amount"])
        date_paid = parse_date(payload["datePaid"])
        date_incurred = (
            parse_date(payload["dateIncurred"])
            if payload["dateIncurred"]
            else date_paid
        )
        source = payload["source"]
        category = payload["category"]
        notes = payload["notes"]

        if source:
            # The `newTag` field from Select2 flags whether the vendor is newly-created
            # or an existing database row.
            if source.get("newTag", False):
                source = db.insert("debit_sources", {"name": source["text"]})
            else:
                source_id = source["id"]
        else:
            source = None

        if category.get("newTag", False):
            category_id = db.insert("debit_categories", {"category": category["text"]})
        else:
            category_id = category["id"]

        entry = db.insert_and_get(
            "debits",
            {
                "amount": amount,
                "date_paid": date_paid,
                "date_incurred": date_incurred,
                "source": source_id,
                "category": category_id,
                "notes": notes,
            },
            get_related=True,
        )
        return JsonResponse(entry, encoder=CustomJSONEncoder)


def credit_categories_get(request: HttpRequest, name: str) -> HttpResponse:
    with Database() as db:
        categories = db.select(
            "credit_categories",
            where="category_slug = :category",
            values={"category": name},
        )
        return JsonResponse(
            {
                "category": categories[0]["category"],
                "subcategories": [
                    {
                        "name": category["subcategory"],
                        "slug": category["subcategory_slug"],
                    }
                    for category in categories
                ],
            }
        )


def credit_subcategories_get(
    request: HttpRequest, category_name: str, subcategory_name: str
) -> HttpResponse:
    with Database() as db:
        categories = db.select(
            "credit_categories",
            where="category_slug = :category",
            values={"category": category_name},
        )
        subcategory = [
            c for c in categories if c["subcategory_slug"] == subcategory_name
        ][0]
        return JsonResponse(
            {
                "category": subcategory["category"],
                "subcategory": subcategory["subcategory"],
                "subcategories": [
                    {
                        "name": category["subcategory"],
                        "slug": category["subcategory_slug"],
                    }
                    for category in categories
                ],
            }
        )


def autocomplete_credit_categories(request: HttpRequest) -> HttpResponse:
    with Database(readonly=True) as db:
        query = request.GET.get("q", "")
        return JsonResponse(
            autocomplete_generic(
                db,
                query,
                "credit_categories",
                lambda row: f"{row['category']} / {row['subcategory']}",
            )
        )


def autocomplete_debit_categories(request: HttpRequest) -> HttpResponse:
    with Database(readonly=True) as db:
        query = request.GET.get("q", "")
        return JsonResponse(
            autocomplete_generic(
                db,
                query,
                "debit_categories",
                lambda row: row["category"],
            )
        )


def autocomplete_debit_sources(request: HttpRequest) -> HttpResponse:
    with Database(readonly=True) as db:
        query = request.GET.get("q", "")
        return JsonResponse(
            autocomplete_generic(
                db,
                query,
                "debit_sources",
                lambda row: row["name"],
            )
        )


def autocomplete_vendors(request: HttpRequest) -> HttpResponse:
    with Database(readonly=True) as db:
        query = request.GET.get("q", "")
        return JsonResponse(
            autocomplete_generic(
                db,
                query,
                "vendors",
                lambda row: row["name"],
            )
        )


def autocomplete_generic(
    db: Database, query: str, table: str, stringifier: Callable[[Row], str]
) -> dict:
    query = query.lower()
    results = [
        (row["id"], stringifier(row))
        for row in db.select(table)
        if query in stringifier(row).lower()
    ]
    results.sort(key=lambda pair: pair[1])
    return {"results": [{"id": row[0], "text": row[1]} for row in results]}
