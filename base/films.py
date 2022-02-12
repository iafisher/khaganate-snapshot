from base.database import Database


def watch_film(db: Database, payload: dict):
    # Look for an existing film in the database.
    film = db.get(
        "films",
        where="""
            title = :title AND
            directors = :directors AND
            (year IS NULL OR year = :year)
        """,
        values={
            "title": payload["title"],
            "directors": payload["directors"],
            "year": payload["year"],
        },
    )

    if film is None:
        # If none exists, create one.
        film = db.insert_and_get(
            "films",
            {
                "title": payload["title"],
                "directors": payload["directors"],
                "year": payload["year"],
                "language": payload["language"],
                "documentary": payload["documentary"],
                "synopsis": payload["synopsis"],
            },
        )
    else:
        # If an existing film was found, check if the payload has an updated year.
        if film["year"] is None and payload["year"] is not None:
            db.update_by_pk("films", film["id"], {"year": payload["year"]})

    return db.insert_and_get(
        "film_entries",
        {
            "film": film["id"],
            "date_viewed": payload["date_viewed"],
            "rating": payload["rating"],
            "notes": payload["notes"],
        },
        get_related=True,
    )
