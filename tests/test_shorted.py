import pytest

from flask.testing import FlaskClient

from shorted.errors import ErrorCodes


@pytest.fixture
def test_create_new_url(client: FlaskClient) -> None:
    data = {
        'url': 'http://localhost:5000/efg'
    }
    response = client.post('/shorten_url', json=data)
    assert response.status_code == 201
    assert response.get_json() == {
        'shortened_url': 'http://shorted.com/3JGsZ8mrnl',
    }


def test_redirect_to_original_url(client: FlaskClient) -> None:
    data = {
        'url': 'http://localhost:5000/efg'
    }
    response = client.post('/shorten_url', json=data)
    shortened_url = response.get_json()['shortened_url']
    response = client.get(shortened_url)
    assert response.status_code == 302
    assert response.location == data['url']


def test_content_type_is_json(client: FlaskClient) -> None:
    response = client.post(
        '/shorten_url',
        content_type='application/xml',
        data='</foo>',
    )
    assert response.status_code == 400
    assert response.get_json()['error'] == ErrorCodes.INVALID_CONTENT_TYPE.name


@pytest.mark.parametrize(
    "invalid_json", [
        'abc',
        {},
        {'foo': 'bar'},
    ],
)
def test_invalid_schema(client: FlaskClient, invalid_json: str) -> None:
    response = client.post('/shorten_url', json=invalid_json)
    assert response.status_code == 400
    assert response.get_json()['error'] == ErrorCodes.INVALID_SCHEMA.name


@pytest.mark.parametrize(
    'invalid_url', [
        'abc',
        'ftp://www.almost.com/foo',
        'http://-ww.almost.com/foo',
        'http://distanthost',
        'http://1234.1.1',
    ]
)
def test_invalid_url(client: FlaskClient, invalid_url: str) -> None:
    response = client.post('/shorten_url', json={'url': invalid_url})
    assert response.status_code == 400
    assert response.get_json()['error'] == ErrorCodes.INVALID_URL.name


@pytest.mark.parametrize(
    'valid_url', [
        'http://www.almost.com/foo',
        'https://w-w.almost.com/foo',
        'http://localhost/foo/bar',
        'http://123.1.1.1/something',
        'http://localhost:5000/'
    ],
)
def test_valid_url(client: FlaskClient, valid_url: str) -> None:
    response = client.post('/shorten_url', json={'url': valid_url})
    assert response.status_code == 201


def test_conflict() -> None:
    # Need to add a mock for this
    pass


def test_no_such_shortcut(client: FlaskClient) -> None:
    data = {
        'url': 'http://localhost:5000/efg'
    }
    response = client.post('/shorten_url', json=data)
    shortened_url = response.get_json()['shortened_url']
    nonexistent_shortened_url = '/'.join(
        shortened_url.split('/')[:-1]
    ) + '/noSuch1'
    response = client.get(nonexistent_shortened_url)
    assert response.status_code == 404
    assert response.get_json()['error'] == ErrorCodes.NO_SUCH_SHORTCUT.name
