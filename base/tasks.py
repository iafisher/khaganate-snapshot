import json
from typing import List

from base.database import Database, Row
from base.utils import CustomJSONEncoder


def get_task(db: Database, task_id: int) -> Row:
    task = db.get_by_pk("tasks", task_id)
    task["comments"] = db.select(
        "task_comments", where="task = :task", values={"task": task["id"]}
    )
    task["time_slots"] = db.select(
        "task_time_slots", where="task = :task", values={"task": task["id"]}
    )
    task["updates"] = db.select(
        "task_updates", where="task = :task", values={"task": task["id"]}
    )

    _set_task_last_updated_at_overall(task)

    return task


def list_tasks(db: Database) -> List[Row]:
    tasks = db.select("tasks")
    comments = db.select("task_comments")
    time_slots = db.select("task_time_slots")
    updates = db.select("task_updates")

    task_map = {}
    for task in tasks:
        task["comments"] = []
        task["time_slots"] = []
        task["updates"] = []
        task["child_tasks"] = []
        task_map[task["id"]] = task

    for comment in comments:
        task = task_map[comment["task"]]
        task["comments"].append(comment)

    for time_slot in time_slots:
        task = task_map[time_slot["task"]]
        task["time_slots"].append(time_slot)

    for update in updates:
        task = task_map[update["task"]]
        task["updates"].append(update)

    for task in tasks:
        _set_task_last_updated_at_overall(task)

    return tasks


def create_task(db, task: Row) -> Row:
    rowid = db.insert("tasks", task)
    return get_task(db, rowid)


def update_task(db: Database, pk: int, updated_task: Row) -> Row:
    task = db.get_by_pk("tasks", pk)
    # TODO(2021-09-28): This is really janky.
    serialized_task = json.loads(CustomJSONEncoder().encode(task))

    db.update_by_pk("tasks", pk, updated_task)
    for key, value in updated_task.items():
        if serialized_task[key] != value:
            db.insert(
                "task_updates",
                {
                    "task": pk,
                    "field": key,
                    "old_value": serialized_task[key] or "",
                    "new_value": value or "",
                },
            )

    return get_task(db, pk)


def _set_task_last_updated_at_overall(task: Row) -> None:
    last_updated_at_overall = task["last_updated_at"]

    for comment in task["comments"]:
        last_updated_at_overall = max(
            last_updated_at_overall, comment["last_updated_at"]
        )

    for time_slot in task["time_slots"]:
        last_updated_at_overall = max(
            last_updated_at_overall, time_slot["last_updated_at"]
        )

    task["last_updated_at_overall"] = last_updated_at_overall


def _simplified_task(task: Row) -> Row:
    return {"id": task["id"], "title": task["title"], "status": task["status"]}
