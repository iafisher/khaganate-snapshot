from django.contrib import admin
from django.urls import path, register_converter

from base import (
    bookmarks,
    books,
    calendar,
    drill,
    films,
    git,
    goals,
    metrics,
    search,
    tasks,
    travel,
)

from . import (
    api_alerts,
    api_bookmarks,
    api_database,
    api_explorer,
    api_finances,
    api_golinks,
    api_journal,
    api_tags,
    converters,
    views,
)
from .adapter import adapt

register_converter(converters.DateConverter, "date")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("go/<path:path>", api_golinks.direct),
    # Generic database APIs
    path("api/db/create/<table>", api_database.create),
    path("api/db/delete/<table>/<int:pk>", api_database.delete),
    path("api/db/get/<table>", api_database.get),
    path("api/db/get/<table>/<int:pk>", api_database.get),
    path("api/db/list/<table>", api_database.list),
    path("api/db/sql", api_database.sql),
    path("api/db/update/<table>/<int:pk>", api_database.update),
    # Books APIs
    path("api/books/finish/<int:pk>", adapt(books.finish_book, post=True)),
    path("api/books/list", adapt(books.list_books)),
    path("api/books/list/<int:year>", adapt(books.list_books)),
    path("api/books/list/<int:year>/<int:month>", adapt(books.list_books)),
    path("api/books/start", adapt(books.start_book, post=True)),
    path(
        "api/books/recommendations/start/<int:pk>",
        adapt(books.start_recommendation, post=True),
    ),
    # Biblio APIs
    path(
        "api/bookmarks/topics/get/<path:path>",
        adapt(bookmarks.get_topic),
    ),
    path(
        "api/bookmarks/topics/get-for-bookmark/<int:pk>",
        adapt(bookmarks.get_bookmark_topics),
    ),
    path(
        "api/bookmarks/update/<int:pk>",
        adapt(bookmarks.update_bookmark, post=True),
    ),
    # Calendar APIs
    path(
        "api/calendar/events/list/<date:start>/<date:end>",
        adapt(calendar.list_calendar_events),
    ),
    # Drill APIs
    path("api/drill/get", adapt(drill.get_quiz)),
    path("api/drill/submit", adapt(drill.submit_quiz, post=True)),
    # Films APIs
    path("api/films/watch", adapt(films.watch_film, post=True)),
    # Git APIs
    path("api/git/diff/<path:path>", adapt(git.get_diff, database=False)),
    # Goals APIs
    path("api/goals/list/<int:year>/<int:month>", adapt(goals.list_current)),
    # Metrics APIs
    path("api/metrics/get/<metric_name>", adapt(metrics.get_metric)),
    path("api/metrics/list/<int:year>/<int:month>", adapt(metrics.list_metrics)),
    # Search APIs
    path("api/search", adapt(search.search, query_parameter="q")),
    # Tasks APIs
    path("api/tasks/create", adapt(tasks.create_task, post=True)),
    path("api/tasks/get/<int:task_id>", adapt(tasks.get_task)),
    path("api/tasks/list", adapt(tasks.list_tasks)),
    path("api/tasks/update/<int:pk>", adapt(tasks.update_task, post=True)),
    # Travel APIs
    path("api/travel/list", adapt(travel.list_visits)),
    path("api/travel/list/<int:year>", adapt(travel.list_visits)),
    path("api/travel/create", adapt(travel.create_visit, post=True)),
    # Specialized APIs
    path("api/alerts/list", api_alerts.list),
    path("api/files/get/", api_explorer.files_get),
    path("api/files/get/<path:path>", api_explorer.files_get),
    path("api/files/raw/<path:path>", api_explorer.files_get_raw),
    path("api/files/save", api_explorer.files_save),
    path("api/journal/entries/<int:year>/<int:month>", api_journal.entries),
    path("api/journal/entries/<int:year>/<int:month>/<int:day>", api_journal.entry),
    path(
        "api/finances/credit-categories/get/<name>", api_finances.credit_categories_get
    ),
    path(
        "api/finances/credit-categories/get/<category_name>/<subcategory_name>",
        api_finances.credit_subcategories_get,
    ),
    path("api/finances/credits/create", api_finances.credits_create),
    path(
        "api/finances/credit-categories/autocomplete",
        api_finances.autocomplete_credit_categories,
    ),
    path("api/finances/debits/create", api_finances.debits_create),
    path(
        "api/finances/debit-categories/autocomplete",
        api_finances.autocomplete_debit_categories,
    ),
    path(
        "api/finances/debit-sources/autocomplete",
        api_finances.autocomplete_debit_sources,
    ),
    path("api/finances/vendors/autocomplete", api_finances.autocomplete_vendors),
    path("api/refs/list/<reflist>", api_bookmarks.list),
    path("api/tags/bookmark/create", api_tags.BookmarkCreateView.as_view()),
    path("api/tags/bookmark/delete", api_tags.BookmarkDeleteView.as_view()),
    path("api/tags/bookmark/get", api_tags.BookmarkGetView.as_view()),
    path("api/tags/topic/search", api_tags.TopicSearchView.as_view()),
    # Catch-all routes for frontend routing
    path("api/<path:path>", views.not_found),
    path("", views.vue_app),
    path("<path:path>", views.vue_app),
]
