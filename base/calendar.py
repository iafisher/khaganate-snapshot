import datetime
from typing import List

from base.database import Database, Row
from base.utils import date_range


def list_calendar_events(
    db: Database, start: datetime.date, end: datetime.date
) -> List[Row]:
    events = db.select(
        "calendar_events",
        where=":start <= end_date AND start_date <= :end",
        values={"start": start.isoformat(), "end": end.isoformat()},
    )
    events.extend(get_recurring_events(db, start, end))

    for event in events:
        if event["start"]:
            event["start_minutes"] = event["start"].hour * 60 + event["start"].minute
        else:
            event["start_minutes"] = 0

        if event["end"]:
            event["end_minutes"] = event["end"].hour * 60 + event["end"].minute
        else:
            event["end_minutes"] = 0

    events.sort(key=lambda event: (event["start_date"], event["start_minutes"]))
    return events


def get_recurring_events(
    db: Database, start: datetime.date, end: datetime.date
) -> List[Row]:
    events = []

    recurring_events = db.select(
        "calendar_recurring_events",
        where="""
            (recurrence_start <= :end)
            AND (recurrence_end IS NULL OR recurrence_end < :start)
        """,
        values={"start": start.isoformat(), "end": end.isoformat()},
    )
    for recurring_event in recurring_events:
        events.extend(
            _get_concrete_events_from_recurrence(db, recurring_event, start, end)
        )

    return events


def _get_concrete_events_from_recurrence(
    db: Database, recurring_event: Row, start: datetime.date, end: datetime.date
) -> List[Row]:
    recurrence_exception_list = db.select(
        "calendar_recurring_event_exceptions",
        where="recurring_event = :recurring_event AND :start <= date AND date <= :end",
        values={
            "recurring_event": recurring_event["id"],
            "start": start.isoformat(),
            "end": end.isoformat(),
        },
    )
    recurrence_exception_map = {
        exception["date"].isoformat(): exception
        for exception in recurrence_exception_list
    }

    events = []
    for date in date_range(start, end):
        # Check if the recurring event has an exception row.
        if date.isoformat() in recurrence_exception_map:
            exception = recurrence_exception_map[date.isoformat()]
            # Missing `start` and `end` columns in an exception row indicate that the
            # event was cancelled.
            if not exception["start"] or not exception["end"]:
                continue

            # Otherwise, the start or end of the event was modified.
            modified_event = recurring_event.copy()
            modified_event["start"] = exception["start"]
            modified_event["end"] = exception["end"]
            modified_event["start_date"] = exception["date"]
            modified_event["end_date"] = exception["date"]
            events.append(modified_event)
            continue

        recurrence_start = recurring_event["recurrence_start"]
        converted_event = _convert_recurring_event(date, recurring_event)
        if recurring_event["recurrence"] == "weekdays":
            if date.weekday() < 5:
                events.append(converted_event)
        elif recurring_event["recurrence"] == "weekly":
            if date.weekday() == recurrence_start.weekday():
                events.append(converted_event)
        elif recurring_event["recurrence"] == "yearly":
            if (
                date.month == recurrence_start.month
                and date.day == recurrence_start.day
            ):
                events.append(converted_event)
        else:
            raise ValueError(recurring_event["recurrence"])

    return events


def _convert_recurring_event(date: datetime.date, recurring_event: Row) -> Row:
    return {
        "id": recurring_event["id"],
        "title": recurring_event["title"],
        "description": recurring_event["description"],
        "location": recurring_event["location"],
        "start_date": date,
        "end_date": date,
        "start": recurring_event["start"],
        "end": recurring_event["end"],
        "recurring": True,
        "created_at": recurring_event["created_at"],
        "last_updated_at": recurring_event["last_updated_at"],
    }
