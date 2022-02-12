"""
Khaganate's database schema, defined using isqlite.

To migrate the database to match the schema, run ``kgdb migrate base/schema.py``. This
will display a list of changes that would be made. To actually make the changes, re-run
the command with the ``--write`` option.

Further documentation: https://isqlite.readthedocs.io/en/latest/schemas.html
"""
from isqlite import AutoTable as IsqliteAutoTable
from isqlite import OnDelete, Schema, columns


def AutoTable(*args, **kwargs):
    return IsqliteAutoTable(*args, use_epoch_timestamps=True, **kwargs)


SCHEMA = Schema(
    [
        AutoTable(
            "books",
            columns=[
                columns.text("title"),
                columns.text("authors"),
                columns.integer("year", required=False),
                columns.text("edition", required=False),
                columns.boolean("fictional"),
                columns.integer("pages", required=False),
                columns.text("kg_link", required=False),
            ],
        ),
        AutoTable(
            "book_entries",
            columns=[
                columns.foreign_key("book", foreign_table="books"),
                columns.date("date_started"),
                columns.date("date_ended", required=False),
                columns.boolean("abandoned"),
                columns.boolean("skimmed", default=False),
                columns.decimal("rating", required=False),
            ],
        ),
        AutoTable(
            "book_recommendations",
            columns=[
                columns.foreign_key("book", foreign_table="books"),
                columns.text("recommender", required=False),
                columns.text("pitch", required=False),
                columns.date("date_added"),
                columns.date("date_removed", required=False),
            ],
        ),
        AutoTable(
            "bookmarks",
            columns=[
                columns.text("title"),
                columns.text("url", required=False),
                columns.text("author", required=False),
                columns.integer("year", required=False),
                # 1 = average, 2 = good, 3 = exceptional
                columns.integer("quality", required=False, min=1, max=3, default=1),
                columns.text("keywords", required=False),
                # The relative path to an on-disk copy of a bookmarked PDF, relative to
                # constants.FILES.
                columns.text("pdf", required=False),
                columns.text("annotation", required=False),
            ],
        ),
        AutoTable(
            "bookmark_topics",
            columns=[
                columns.text("path", unique=True),
            ],
        ),
        AutoTable(
            "bookmark_topic_relations",
            columns=[
                columns.foreign_key("bookmark", foreign_table="bookmarks"),
                columns.foreign_key("topic", foreign_table="bookmark_topics"),
            ],
        ),
        AutoTable(
            "calendar_events",
            columns=[
                columns.date("start_date"),
                columns.date("end_date"),
                columns.time("start", required=False),
                columns.time("end", required=False),
                columns.integer("travel_time", required=False, min=0, default=0),
                columns.text("title"),
                columns.text("description", required=False),
                columns.text("location", required=False),
                columns.boolean("maybe", default=False),
            ],
        ),
        AutoTable(
            "calendar_recurring_events",
            columns=[
                columns.time("start"),
                columns.time("end"),
                columns.text("title"),
                columns.text("description", required=False),
                columns.text("location", required=False),
                columns.text("recurrence", choices=["weekdays", "weekly", "yearly"]),
                columns.date("recurrence_start"),
                columns.date("recurrence_end", required=False),
            ],
        ),
        AutoTable(
            "calendar_recurring_event_exceptions",
            columns=[
                columns.foreign_key(
                    "recurring_event",
                    foreign_table="calendar_recurring_events",
                    on_delete=OnDelete.CASCADE,
                ),
                columns.date("date"),
                columns.time("start", required=False),
                columns.time("end", required=False),
            ],
        ),
        AutoTable(
            "counties",
            columns=[
                columns.text("name"),
                columns.text("state"),
            ],
        ),
        AutoTable(
            "county_visits",
            columns=[
                columns.foreign_key("county", foreign_table="counties"),
                columns.date("date", required=False),
                columns.date("date_end", required=False),
                columns.boolean("only_year", default=False),
                columns.text(
                    "visit_type",
                    choices=(
                        "traveled through",
                        "visited",
                        "spent the night",
                        "resided",
                    ),
                ),
                # Whether the visits were intermittent, i.e. not every day in the time
                # period.
                columns.boolean("is_intermittent", default=False),
            ],
        ),
        AutoTable(
            "credits",
            columns=[
                columns.date("date_paid"),
                columns.date("date_incurred", required=False),
                columns.decimal("amount"),
                columns.foreign_key("vendor", foreign_table="vendors", required=False),
                columns.foreign_key("category", foreign_table="credit_categories"),
                columns.text("payment_method"),
                columns.text("notes", required=False),
            ],
        ),
        AutoTable(
            "credit_categories",
            columns=[
                columns.text("category"),
                columns.text("subcategory"),
                columns.text("category_slug"),
                columns.text("subcategory_slug"),
            ],
        ),
        AutoTable(
            "daily_task_singleton",
            columns=[],
        ),
        AutoTable(
            "debits",
            columns=[
                columns.date("date_paid"),
                columns.date("date_incurred", required=False),
                columns.decimal("amount"),
                columns.foreign_key(
                    "source", foreign_table="debit_sources", required=False
                ),
                columns.foreign_key("category", foreign_table="debit_categories"),
                columns.text("notes", required=False),
            ],
        ),
        AutoTable(
            "debit_categories",
            columns=[
                columns.text("category", unique=True),
            ],
        ),
        AutoTable(
            "debit_sources",
            columns=[
                columns.text("name", unique=True),
            ],
        ),
        AutoTable(
            "films",
            columns=[
                columns.text("title"),
                columns.text("directors", required=False),
                columns.integer("year", required=False),
                columns.text("language", required=False),
                columns.boolean("documentary"),
                columns.text("synopsis", required=False),
                columns.text("kg_link", required=False),
            ],
        ),
        AutoTable(
            "film_entries",
            columns=[
                columns.foreign_key("film", foreign_table="films"),
                columns.date("date_viewed"),
                columns.decimal("rating", required=False),
                columns.text("notes", required=False),
            ],
        ),
        AutoTable(
            "film_recommendations",
            columns=[
                columns.foreign_key("film", foreign_table="films"),
                columns.text("recommender", required=False),
                columns.text("pitch", required=False),
                columns.date("date_added"),
                columns.date("date_removed", required=False),
            ],
        ),
        AutoTable(
            "goals",
            columns=[
                columns.text("title"),
                columns.text("timespan", choices=("month", "quarter", "year")),
                columns.date("date"),
                columns.integer("progress", required=False),
                columns.integer("max_progress", default=10),
                columns.foreign_key(
                    "progress_from_task", foreign_table="tasks", required=False
                ),
                columns.text("progress_from_metric", required=False),
                # Set to true for metrics where progress is negative, e.g., "Eat out
                # fewer than ten times".
                columns.boolean("metric_is_maximum", default=0),
            ],
        ),
        AutoTable(
            "golinks",
            columns=[
                columns.text("link_text", unique=True),
                columns.text("path"),
            ],
        ),
        AutoTable(
            "golink_visits",
            columns=[
                columns.foreign_key("golink", foreign_table="golinks"),
            ],
        ),
        AutoTable(
            "habits",
            columns=[
                columns.text("name"),
                columns.integer("points"),
                columns.boolean("deprecated", default=False),
            ],
        ),
        AutoTable(
            "habit_entries",
            columns=[
                columns.date("date"),
                columns.foreign_key("habit", foreign_table="habits"),
                columns.text("name"),
                columns.integer("points"),
            ],
        ),
        AutoTable(
            "journal_entries",
            columns=[
                columns.date("date", unique=True),
                columns.text("text"),
            ],
        ),
        AutoTable(
            "metrics",
            columns=[
                columns.text("name"),
                columns.date("month"),
                columns.decimal("value"),
            ],
        ),
        AutoTable(
            "quizzes",
            columns=[
                columns.text("name", unique=True),
                columns.boolean("disabled", default=False),
                columns.integer("time_last_taken", default=0),
            ],
        ),
        AutoTable(
            "quiz_questions",
            columns=[
                columns.foreign_key("quiz", foreign_table="quizzes"),
                columns.text("text"),
                columns.text("answer"),  # a JSON list
                columns.text("choices", required=False),  # a JSON list
                columns.text(
                    "type",
                    choices=(
                        "multiple-choice",
                        "unordered-list",
                        "ordered-list",
                        "short-answer",
                    ),
                ),
                columns.integer("strength", default=0, min=0, max=10),
                columns.boolean("deprecated", default=False),
                columns.integer("time_last_asked", default=0),
            ],
        ),
        AutoTable(
            "quiz_results",
            columns=[
                columns.foreign_key("question", foreign_table="quiz_questions"),
                columns.integer("score"),
                columns.integer("time_asked"),
            ],
        ),
        AutoTable(
            "tasks",
            columns=[
                columns.text("title"),
                columns.text("description", required=False),
                columns.date("deadline", required=False),
                columns.text(
                    "status",
                    default="open",
                    choices=(
                        "open",
                        "fixed",
                        "wontfix",
                        "obsolete",
                        "duplicate",
                    ),
                ),
                columns.integer("priority", required=True, min=0, max=4, default=3),
                columns.boolean("is_machine_created", default=False),
            ],
        ),
        AutoTable(
            "task_comments",
            columns=[
                columns.foreign_key("task", foreign_table="tasks"),
                columns.text("text"),
            ],
        ),
        AutoTable(
            "task_time_slots",
            columns=[
                columns.foreign_key("task", foreign_table="tasks"),
                columns.date("date"),
                columns.integer("minutes"),
            ],
        ),
        AutoTable(
            "task_updates",
            columns=[
                columns.foreign_key("task", foreign_table="tasks"),
                columns.text("field"),
                columns.text("old_value", required=False),
                columns.text("new_value", required=False),
            ],
        ),
        AutoTable(
            "vendors",
            columns=[
                columns.text("name", unique=True),
                columns.boolean("is_local_business", required=False),
            ],
        ),
    ]
)
