import datetime
import glob
import os
from django.http import HttpRequest, HttpResponse, JsonResponse

from base import constants
from base.database import Database
from base.utils import format_time, remove_suffix


def list(request: HttpRequest) -> HttpResponse:
    alerts = []

    failed_log_files = glob.glob(os.path.join(constants.LOGS_FOLDER, "*.FAIL"))
    for failed_log_file in failed_log_files:
        path = remove_suffix(failed_log_file, ".FAIL")
        alerts.append({"message": f"Log file alert: {path}", "level": "severe"})

    with Database(readonly=True) as db:
        today = datetime.date.today()
        now = datetime.datetime.now()
        in_two_hours = now + datetime.timedelta(minutes=120)
        events = db.select(
            "calendar_events",
            where="start_date = :today AND start <= :in_two_hours AND start >= :now",
            values={
                "today": today,
                "in_two_hours": in_two_hours.time(),
                "now": now.time(),
            },
        )

        for event in events:
            title = event["title"]
            start = format_time(event["start"])
            alerts.append({"message": f"{title} starting at {start}", "level": "info"})

    return JsonResponse(alerts, safe=False)
