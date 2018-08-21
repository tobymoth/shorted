import pytest

from shorted.algorithms import base62


@pytest.mark.parametrize("test_input,expected", [
    (0, '0'),
    (9, '9'),
    (10, 'a'),
    (35, 'z'),
    (36, 'A'),
    (61, 'Z'),
    (62, '10'),
    (62 * 62, '100'),
    (62 * 62 + 1, '101'),
    ])
def test_base62(test_input: int, expected: str) -> None:
    assert base62(test_input) == expected
