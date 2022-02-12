import glob
import html
import logging
import os
import shutil
from typing import Any, Dict, Iterator, List, Optional, Tuple

from base import constants
from base.database import Database
from base.utils import get_short_file_path
from whoosh import fields, index, qparser
from whoosh.analysis import StandardAnalyzer
from whoosh.query import QueryError

logger = logging.getLogger(__name__)

BASE_BOOKMARK_WEIGHT = 10
DEFAULT_WEIGHT = 10
ARCHIVED_FILE_WEIGHT = 0
READING_ENTRY_WEIGHT = 0
VIEWING_ENTRY_WEIGHT = 0
TRANSACTION_WEIGHT = 0
TASK_WEIGHT = 0


def search(db: Database, query: str) -> List[Dict[str, Any]]:
    ix = index.open_dir(constants.SEARCH_INDEX)
    with ix.searcher() as searcher:
        # Search on the title, content, and keywords fields by default, falling back on
        # title and content only if an error occurs.
        #
        # An error will occur on double-quoted search queries because the keywords
        # field does not support those.
        try:
            results = _search_on_fields(
                ["title", "content", "keywords"], query, ix.schema, searcher
            )
        except QueryError:
            results = _search_on_fields(
                ["title", "content"], query, ix.schema, searcher
            )

    for result in results:
        result["preview"] = _get_preview(db, result, query)

    return results


def rebuild_index(*, verbose: bool = False) -> int:
    if os.path.exists(constants.SEARCH_INDEX):
        shutil.rmtree(constants.SEARCH_INDEX)
    os.mkdir(constants.SEARCH_INDEX)

    schema = _get_schema()
    ix = index.create_in(constants.SEARCH_INDEX, schema)
    writer = ix.writer()

    with Database(readonly=True) as db:
        count = 0
        for document in _get_documents(db):
            if verbose:
                print(f"Indexing document: {document['id']}")

            writer.add_document(**document)
            count += 1

    writer.commit()
    return count


def update_index(*, verbose: bool = False) -> Tuple[int, int]:
    # Based on https://whoosh.readthedocs.io/en/latest/indexing.html#incremental-indexing
    ix = index.open_dir(constants.SEARCH_INDEX)
    ids = set()
    to_be_indexed = set()

    with Database(readonly=True) as db:
        with ix.searcher() as searcher:
            writer = ix.writer()
            for entry in searcher.all_stored_fields():
                indexed_id = entry["id"]
                ids.add(indexed_id)

                last_updated_at = _get_document_last_updated_at(db, indexed_id)
                if last_updated_at is None:
                    writer.delete_by_term("id", indexed_id)
                elif last_updated_at > entry["lastUpdatedAt"]:
                    writer.delete_by_term("id", indexed_id)
                    to_be_indexed.add(indexed_id)

            total = 0
            updated = 0
            for document in _get_documents(db):
                total += 1
                if document["id"] in to_be_indexed or document["id"] not in ids:
                    if verbose:
                        print(f"Indexing document: {document['id']}")

                    updated += 1
                    writer.add_document(**document)

            writer.commit()
            return updated, total


def _get_preview(db: Database, result, query: str) -> Optional[str]:
    if result["id"].startswith("file:"):
        path = get_short_file_path(result["id"][5:])
        result["path"] = path

        with open(os.path.join(constants.FILES, path), "r", encoding="utf8") as f:
            text = f.read()
            return _get_preview_from_text(text, query)
    elif result["id"].startswith("db:journal_entries:"):
        journal_entry = _get_database_row_from_result(db, result)
        if journal_entry is not None:
            return _get_preview_from_text(journal_entry["text"], query)
    elif result["id"].startswith("db:bookmarks:"):
        bookmark = _get_database_row_from_result(db, result)
        if bookmark is not None:
            return _get_preview_from_text(bookmark["annotation"], query)

    return None


def _get_preview_from_text(text: str, query: str) -> Optional[str]:
    index = text.lower().find(query.lower())
    if index == -1:
        return None

    start = max(0, index - 50)
    end = min(len(text), index + len(query) + 50)
    return (
        ("..." if start > 0 else "")
        + html.escape(text[start:index])
        + "<mark>"
        + html.escape(text[index : index + len(query)])
        + "</mark>"
        + html.escape(text[index + len(query) : end])
        + ("..." if end < len(text) - 1 else "")
    )


def _get_database_row_from_result(db, result):
    domain, table, pk = result["id"].split(":", maxsplit=2)
    assert domain == "db"
    return db.get_by_pk(table, int(pk))


def _search_on_fields(fields, query, schema, searcher) -> List[dict]:
    parser = qparser.MultifieldParser(fields, schema)
    parsed_query = parser.parse(query)
    logger.debug("Parsed query %r as %r", query, parsed_query)
    return [dict(hit) for hit in searcher.search(parsed_query, limit=None)]


def _get_document_last_updated_at(db: Database, docid: str) -> Optional[float]:
    if docid.startswith("file:"):
        path = docid[5:]
        try:
            return os.path.getmtime(path)
        except FileNotFoundError:
            return None
    elif docid.startswith("db:"):
        _, table, pk = docid.split(":")
        row = db.get_by_pk(table, pk)
        return row["last_updated_at"] if row is not None else None
    else:
        raise ValueError(f"could not parse document ID: {docid!r}")


def _get_schema() -> Any:
    # Use an analyzer with a `minsize` of 1 so that queries like 'malcolm x' work.
    #
    # https://github.com/iafisher/khaganate/issues/642
    analyzer = StandardAnalyzer(minsize=1)
    return fields.Schema(
        id=fields.ID(stored=True),
        title=fields.TEXT(stored=True, field_boost=2.0, analyzer=analyzer),
        content=fields.TEXT(analyzer=analyzer),
        keywords=fields.KEYWORD(
            stored=True,
            lowercase=True,
            scorable=True,
            field_boost=3.0,
            analyzer=analyzer,
        ),
        # STORED fields are stored with the document but not indexed or searchable.
        url=fields.STORED,
        weight=fields.STORED,
        type=fields.STORED,
        hasMarkdownTitle=fields.STORED,
        lastUpdatedAt=fields.STORED,
    )


def _get_documents(db: Database) -> Iterator[Dict[str, Any]]:
    md_glob_path = constants.FILES + "/**/*.md"
    for path in glob.iglob(md_glob_path, recursive=True):
        with open(path, "r", encoding="utf8") as f:
            body = f.read()

        if body.startswith("#"):
            end_of_first_line = body.find("\n")
            if end_of_first_line == -1:
                title = ""
            else:
                title = body[1:end_of_first_line].strip()
        else:
            title = ""

        file_type = "file"
        weight = ARCHIVED_FILE_WEIGHT if "/archive/" in path else BASE_BOOKMARK_WEIGHT

        yield {
            "id": "file:" + path,
            "title": title or "files/" + get_short_file_path(path),
            "content": body,
            "type": file_type,
            "weight": weight,
            "hasMarkdownTitle": bool(title),
            "lastUpdatedAt": os.path.getmtime(path),
        }

    txt_glob_path = constants.FILES + "/**/*.txt"
    for path in glob.iglob(txt_glob_path, recursive=True):
        with open(path, "r", encoding="utf8") as f:
            body = f.read()

        yield {
            "id": "file:" + path,
            "title": "files/" + get_short_file_path(path),
            "content": body,
            "type": "file",
            "weight": ARCHIVED_FILE_WEIGHT
            if "/archive/" in path
            else BASE_BOOKMARK_WEIGHT,
            "hasMarkdownTitle": False,
            "lastUpdatedAt": os.path.getmtime(path),
        }

    books_added = set()
    for reading_entry in db.select("book_entries", get_related=["book"]):
        book = reading_entry["book"]
        if book["id"] in books_added:
            continue
        else:
            books_added.add(book["id"])

        d = reading_entry["date_started"]
        yield {
            "id": f"db:book_entries:{reading_entry['id']}",
            "title": f"{book['title']} (by {book['authors']}) started {d.isoformat()}",
            "url": f"/reading/{d.year}/{d.month:0>2}",
            "type": "book",
            "weight": READING_ENTRY_WEIGHT,
            "hasMarkdownTitle": False,
            "lastUpdatedAt": reading_entry["last_updated_at"],
        }

    films_added = set()
    for viewing_entry in db.select("film_entries", get_related=["film"]):
        film = viewing_entry["film"]
        if film["id"] in films_added:
            continue
        else:
            films_added.add(film["id"])

        d = viewing_entry["date_viewed"]
        yield {
            "id": f"db:film_entries:{viewing_entry['id']}",
            "title": f"{film['title']} (by {film['directors']})",
            "url": f"/watching/{d.year}",
            "type": "film",
            "weight": VIEWING_ENTRY_WEIGHT,
            "hasMarkdownTitle": False,
            "lastUpdatedAt": viewing_entry["last_updated_at"],
        }

    for journal_entry in db.select("journal_entries"):
        yield {
            "id": f"db:journal_entries:{journal_entry['id']}",
            "title": f"Journal, {journal_entry['date'].isoformat()}",
            "content": journal_entry["text"],
            "url": "/journal/" + journal_entry["date"].isoformat().replace("-", "/"),
            "type": "journal",
            "weight": BASE_BOOKMARK_WEIGHT,
            "hasMarkdownTitle": False,
            "lastUpdatedAt": journal_entry["last_updated_at"],
        }

    bookmark_docs = {}
    for bookmark in db.select("bookmarks"):
        bookmark_docs[bookmark["id"]] = {
            "id": f"db:bookmarks:{bookmark['id']}",
            "title": bookmark["title"],
            "content": bookmark["annotation"],
            "url": bookmark["url"],
            "keywords": bookmark["keywords"].split(",") + bookmark["author"].split(","),
            "type": "bookmark",
            "weight": BASE_BOOKMARK_WEIGHT + bookmark["quality"],
            "hasMarkdownTitle": False,
            "lastUpdatedAt": bookmark["last_updated_at"],
        }

    for bookmark in bookmark_docs.values():
        bookmark["keywords"] = ",".join(bookmark["keywords"])
        yield bookmark

    for credit in db.select("credits", get_related=["vendor"]):
        if credit["vendor"] is None:
            continue

        title = (
            f"Transaction: ${credit['amount']:,.2f} paid to "
            + f"{credit['vendor']['name']} "
            + f"on {credit['date_paid'].isoformat()}"
        )
        d = credit["date_incurred"]
        yield {
            "id": f"db:credits:{credit['id']}",
            "title": title,
            "content": credit["notes"],
            "url": f"/finances/{d.year}/{d.month:0>2}",
            "type": "transaction",
            "weight": TRANSACTION_WEIGHT,
            "hasMarkdownTitle": False,
            "lastUpdatedAt": credit["last_updated_at"],
        }

    for task in db.select("tasks"):
        yield {
            "id": f"db:tasks:{task['id']}",
            "title": f"Task: {task['title']}",
            "content": task["description"],
            "url": f"/task/{task['id']}",
            "type": "task",
            "weight": TASK_WEIGHT,
            "hasMarkdownTitle": True,
            "lastUpdatedAt": task["last_updated_at"],
        }

    for comment in db.select("task_comments", get_related=["task"]):
        yield {
            "id": f"db:task_comments:{comment['id']}",
            "title": f"Comment on task: {comment['task']['title']}",
            "content": comment["text"],
            "url": f"/task/{comment['task']['id']}",
            "type": "task comment",
            "weight": TASK_WEIGHT,
            "hasMarkdownTitle": True,
            "lastUpdatedAt": comment["last_updated_at"],
        }

    for calendar_event in db.select("calendar_events"):
        yield {
            "id": f"db:calendar_events:{calendar_event['id']}",
            "title": f"{calendar_event['title']} ({calendar_event['start_date']})",
            "content": calendar_event["description"],
            "url": "/calendar/"
            + calendar_event["start_date"].isoformat().replace("-", "/"),
            "type": "event",
            "weight": BASE_BOOKMARK_WEIGHT,
            "hasMarkdownTitle": True,
            "lastUpdatedAt": calendar_event["last_updated_at"],
        }
