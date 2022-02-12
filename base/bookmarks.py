from typing import List, Optional

from base.database import Database, Row


def get_topic(db: Database, path: str) -> Optional[Row]:
    subtopics = db.select(
        "bookmark_topics",
        where="path LIKE :path_prefix",
        values={"path_prefix": path + "/%"},
    )

    topic = db.get("bookmark_topics", where="path = :path", values={"path": path})
    if topic is not None:
        bookmarks = db.sql(
            """
            SELECT
              bookmarks.id,
              bookmarks.title,
              bookmarks.url,
              bookmarks.quality,
              bookmarks.pdf,
              bookmarks.annotation,
              bookmarks.created_at
            FROM
              bookmarks
            INNER JOIN
              bookmark_topic_relations
            ON
              bookmark_topic_relations.bookmark = bookmarks.id
            WHERE
              bookmark_topic_relations.topic = :topic
            """,
            values={"topic": topic["id"]},
        )
    else:
        bookmarks = []

    return {"bookmarks": bookmarks, "subtopics": subtopics}


def get_bookmark_topics(db: Database, pk: int) -> List[str]:
    return [
        row["path"]
        for row in db.sql(
            """
            SELECT
              bookmark_topics.path
            FROM
              bookmark_topic_relations
            INNER JOIN
              bookmark_topics
            ON
              bookmark_topic_relations.topic = bookmark_topics.id
            WHERE
              bookmark_topic_relations.bookmark = :bookmark
        """,
            values={"bookmark": pk},
        )
    ]


def update_bookmark(db: Database, pk: int, payload: dict) -> Row:
    db.delete(
        "bookmark_topic_relations",
        where="bookmark = :bookmark",
        values={"bookmark": pk},
    )
    for topic in payload["topics"]:
        topic_row = db.get_or_insert("bookmark_topics", {"path": topic})
        db.insert(
            "bookmark_topic_relations", {"bookmark": pk, "topic": topic_row["id"]}
        )

    return db.update_by_pk("bookmarks", pk, {"annotation": payload["annotation"]})
