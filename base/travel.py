import datetime
from typing import Any, Dict, List, Optional

from base.database import Database, Row
from base.utils import parse_date


def list_visits(db: Database, year: Optional[int] = None) -> List[Dict[str, Any]]:
    counties = []
    for county in db.select("counties"):
        if year:
            visits = db.select(
                "county_visits",
                where="county = :county AND date <= :year_end AND "
                + "(date_end >= :year_start OR date_end IS NULL)",
                values={
                    "county": county["id"],
                    "year_start": f"{year}-01-01",
                    "year_end": f"{year}-12-31",
                },
            )
        else:
            visits = db.select(
                "county_visits",
                where="county = :county",
                values={"county": county["id"]},
            )

        if not visits:
            continue

        counties.append(
            {
                "county": county["name"],
                "state": county["state"],
                "visits": [
                    {
                        "type": visit["visit_type"],
                        "date": visit["date"],
                        "dateEnd": visit["date_end"],
                        "yearOnly": visit["only_year"],
                        "isIntermittent": visit["is_intermittent"],
                    }
                    for visit in sorted(
                        visits,
                        key=lambda v: v["date"]
                        if v["date"] is not None
                        else datetime.date(1970, 1, 1),
                    )
                ],
            }
        )

    return counties


def create_visit(db: Database, payload: Dict[str, Any]) -> Row:
    county, state = payload["county"].split("__", maxsplit=1)

    county_pk = db.get_or_insert("counties", {"name": county, "state": state})["id"]
    date = parse_date(payload["date"])
    return db.insert_and_get(
        "county_visits",
        {
            "county": county_pk,
            "date": date,
            "date_end": date + datetime.timedelta(days=1)
            if payload["type"] == "spent the night"
            else date,
            "only_year": False,
            "visit_type": payload["type"],
        },
    )
