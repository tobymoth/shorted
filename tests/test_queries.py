from sqlalchemy.engine import Connectable

from shorted.queries import maybe_get_url_by_key, probably_upsert_short_url


def test_insert(db: Connectable) -> None:
    key = 'graVy'
    url = 'http://www.train.com'
    assert probably_upsert_short_url(
        db,
        key,
        url,
    )


def test_upsert_idempotent(db: Connectable) -> None:
    key = 'graVy'
    url = 'http://www.train.com'
    assert probably_upsert_short_url(
        db,
        key,
        url,
    )
    assert probably_upsert_short_url(
        db,
        key,
        url,
    )


def test_upsert_spots_conflicts(db: Connectable) -> None:
    key = 'nice'
    url = 'http://www.one.com'
    assert probably_upsert_short_url(db, key, url)
    assert not probably_upsert_short_url(db, key, 'http://www.cyril.com')


def test_get_url_by_key(db: Connectable) -> None:
    key = 'jelly'
    url = 'www.beans.com'
    probably_upsert_short_url(db, key, url)
    assert maybe_get_url_by_key(db, key) == url


def test_no_key_no_url(db: Connectable) -> None:
    key = 'jelly'
    assert maybe_get_url_by_key(db, key) is None


def test_no_url_for_key(db: Connectable) -> None:
    assert not maybe_get_url_by_key(db, 'bianco')
