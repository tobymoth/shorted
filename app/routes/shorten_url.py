import re
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

from flask import current_app, Blueprint, jsonify, Response, redirect, request

from shorted.errors import ErrorCodes


blueprint = Blueprint('shorten_url', __name__)


JSON = Dict[str, str]
CodedResponse = Tuple[Response, int]


@blueprint.route('/shorten_url', methods=['POST'])
def create_short_url() -> CodedResponse:

    def maybe_get_json() -> Optional[JSON]:
        json = request.get_json()
        if json is None or not isinstance(json, dict) or 'url' not in json:
            return None
        return json

    content_type = request.content_type
    if content_type != 'application/json':
        return make_error(
            ErrorCodes.INVALID_CONTENT_TYPE,
            description=f'Content type is {content_type} but should be "application/json"',  # noqa: E501
        )
    json = maybe_get_json()
    if json is None:
        return make_error(
            ErrorCodes.INVALID_SCHEMA,
            description=f'Body is not a JSON object containing a "url" field: {json}',  # noqa: E501
        )
    original_url = json['url']
    original_url = normalise_url(original_url)
    if not is_valid_url(original_url):
        return make_error(
            ErrorCodes.INVALID_URL,
            description=f'The following is not a valid URL: {original_url}',
        )
    shortened_url = current_app.shortener.create_short_url(original_url)
    if shortened_url is None:
        return make_error(
            ErrorCodes.CONFLICT,
            'We are unable to create a shortcut for this URL - call us and we will fix',  # noqa: E501
        )
    return (
        jsonify(
            {
                'shortened_url': shortened_url,
            },
        ),
        201,
    )


@blueprint.route('/<string:key>', methods=['GET'])
def redirect_to_original_url(key: str) -> None:
    original_url = current_app.shortener.get_original_url(key)
    if original_url is None:
        return make_error(
            ErrorCodes.NO_SUCH_SHORTCUT,
            description=f'We do not recognise this key: {key}',
            status_code=404,
        )
    return redirect(original_url, code=302)


def make_error(
        error: ErrorCodes,
        description: str,
        status_code: int=400,
) -> Tuple[Response, int]:
    return (
        jsonify(
            {
                'error': error.name,
                'description': description,
            }
        ),
        status_code,
    )


def normalise_url(url: str) -> str:
    if not url.startswith('http'):
        return f'http:{url}'
    return url


# pinched from stack overflow
VALID_URL = re.compile(
    r'^https?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain  # noqa: E501
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE
)


def is_valid_url(url: str) -> bool:
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ('http', 'https') or parsed_url.netloc == '':
        return False
    return VALID_URL.match(url) is not None
