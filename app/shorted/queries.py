from typing import Optional

from sqlalchemy.engine import Connectable
from sqlalchemy.sql import text


def probably_upsert_short_url(
        db: Connectable,
        key: str,
        url: str,
) -> bool:
    upsert = text(
        """
        INSERT INTO urls (key, url)
             VALUES (:key, :url)
        ON CONFLICT (key) DO NOTHING
          RETURNING 1
        """
    )
    with db.begin() as connection:
        # normally we insert one row
        # if attempt to insert same key, value we get a conflict
        inserted = connection.execute(
            upsert,
            key=key,
            url=url,
        ).scalar() == 1
        if inserted:
            return True
        conflict_query = text(
            """
            SELECT url FROM urls WHERE key = :key
            """
        )
        original_url = connection.execute(conflict_query, key=key).scalar()
        return original_url == url


def maybe_get_url_by_key(
        db: Connectable,
        key: str,
) -> Optional[str]:
    query = text(
        """
        SELECT url FROM urls WHERE key = :key
        """
    )
    with db.begin() as connection:
        return connection.execute(
            query, key=key,
        ).scalar()
