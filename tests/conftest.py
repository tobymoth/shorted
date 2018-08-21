import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.engine import Connectable

from run import create_app


@pytest.fixture(scope='session')
def app() -> Flask:
    return create_app()


@pytest.fixture
def client(app: Flask) -> FlaskClient:  # pylint:disable=redefined-outer-name
    return app.test_client()


@pytest.fixture
def db(app: Flask) -> Connectable:  # pylint:disable=redefined-outer-name
    return app.db


@pytest.fixture(autouse=True)
def clean_db(db: Connectable) -> None:  # pylint:disable=redefined-outer-name
    db.execute("DELETE FROM urls")
