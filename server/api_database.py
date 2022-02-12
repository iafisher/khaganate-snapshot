import json
from django.http import HttpRequest, HttpResponse, JsonResponse, QueryDict
from django.views.decorators.http import require_POST
from typing import Any, Dict, Optional, Tuple

from base.database import Database
from base.utils import CustomJSONEncoder
from sqliteparser import quote

from .adapter import _convert_request_payload


def get(request: HttpRequest, table: str, pk: Optional[int] = None) -> HttpResponse:
    table = _convert_table_name(table)
    with Database() as db:
        if pk is not None:
            return JsonResponse(
                db.get_by_pk(table, pk, get_related=True),
                encoder=CustomJSONEncoder,
                # Necessary because `db.get` may return None.
                safe=False,
            )
        else:
            where, values = _convert_request_to_sql_filter(request.GET)
            return JsonResponse(
                db.get(
                    table,
                    where=where,
                    values=values,
                    get_related=True,
                ),
                encoder=CustomJSONEncoder,
                # Necessary because `db.get` may return None.
                safe=False,
            )


def list(request: HttpRequest, table: str) -> HttpResponse:
    table = _convert_table_name(table)
    with Database() as db:
        where, values = _convert_request_to_sql_filter(request.GET)
        order_by = request.GET.get("__order_by")
        limit_as_string = request.GET.get("__limit")
        get_related = "__no_get_related" not in request.GET

        limit = int(limit_as_string) if limit_as_string is not None else None
        descending = True if "__order_desc" in request.GET else None
        return JsonResponse(
            db.select(
                table,
                where=where,
                values=values,
                order_by=order_by,
                descending=descending,
                get_related=get_related,
                limit=limit,
            ),
            encoder=CustomJSONEncoder,
            safe=False,
        )


@require_POST
def create(request: HttpRequest, table: str) -> HttpResponse:
    table = _convert_table_name(table)
    with Database() as db:
        payload = json.loads(request.body, encoding="utf8")
        payload = _convert_request_payload(payload)
        pk = db.insert(table, payload)
        return JsonResponse(
            db.get(
                table,
                where=f"{table}.id = :id",
                values={"id": pk},
                get_related=True,
            ),
            encoder=CustomJSONEncoder,
        )


@require_POST
def update(request: HttpRequest, table: str, pk: int) -> HttpResponse:
    table = _convert_table_name(table)
    with Database() as db:
        payload = json.loads(request.body, encoding="utf8")
        payload = _convert_request_payload(payload)
        db.update_by_pk(table, pk, payload)
        return JsonResponse(db.get_by_pk(table, pk), encoder=CustomJSONEncoder)


@require_POST
def delete(request: HttpRequest, table: str, pk: int) -> HttpResponse:
    table = _convert_table_name(table)
    with Database() as db:
        db.delete_by_pk(table, pk)
        return JsonResponse({})


@require_POST
def sql(request: HttpRequest) -> HttpResponse:
    payload = json.loads(request.body, encoding="utf8")
    with Database() as db:
        values = payload.get("values", None)
        rows = db.sql(payload["sql"], values=values)
        return JsonResponse(rows, encoder=CustomJSONEncoder, safe=False)


def _convert_request_to_sql_filter(
    getparams: QueryDict,
) -> Tuple[Optional[str], Dict[str, Any]]:
    if getparams:
        values = {}
        where_clauses = []
        for i, (column, value) in enumerate(getparams.items()):
            if column.startswith("__"):
                continue

            sql_value = None
            if "__" in column:
                column, modifier = column.split("__", maxsplit=1)
                if modifier == "contains":
                    operator = "LIKE"
                    sql_value = f"%{value}%"
                elif modifier == "endswith":
                    operator = "LIKE"
                    sql_value = f"%{value}"
                elif modifier == "startswith":
                    operator = "LIKE"
                    sql_value = f"{value}%"
                elif modifier == "null":
                    operator = "IS"
                    sql_value = None
                elif modifier == "not_null":
                    operator = "IS NOT"
                    sql_value = None
                elif modifier == "gt":
                    operator = ">"
                    sql_value = value
                elif modifier == "ge":
                    operator = ">="
                    sql_value = value
                elif modifier == "lt":
                    operator = "<"
                    sql_value = value
                elif modifier == "le":
                    operator = "<="
                    sql_value = value
                else:
                    raise ValueError(f"unknown query modifier: {modifier!r}")
            else:
                operator = "="
                sql_value = value

            placeholder = f"v{i}"
            where_clauses.append(f"{quote(column)} {operator} :{placeholder}")
            values[placeholder] = sql_value
        where = " AND ".join(where_clauses)
        return where, values
    else:
        return None, {}


def _convert_table_name(table):
    return table.replace("-", "_")
