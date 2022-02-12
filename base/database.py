"""
A thin wrapper around the ``isqlite.Database`` API to automatically use some Khaganate-
specific settings.
"""
from typing import Any, Dict

from base import constants
from isqlite import Database as ISqliteDatabase


class Database(ISqliteDatabase):
    def __init__(self, *args, **kwargs) -> None:
        return super().__init__(
            constants.DATABASE_PATH,
            *args,
            # The database schema uses `AutoTable` which automatically creates
            # `created_at` and `last_updated_at` columns, so we tell the database to
            # automatically populate these columns on create and update requests.
            insert_auto_timestamp_columns=["created_at", "last_updated_at"],
            update_auto_timestamp_columns=["last_updated_at"],
            use_epoch_timestamps=True,
            **kwargs
        )


Row = Dict[str, Any]
