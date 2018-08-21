from typing import List


def base62(value: int) -> str:
    """Map a non-negative integer to a sequence comprising [A-Za-z0-9].

       Will call this sequence base 62.
    """
    def translate(character: int) -> str:
        if character < 10:
            return chr(ord('0') + character)
        if character < 36:
            return chr(ord('a') + character - 10)
        return chr(ord('A') + character - 36)

    base = 62
    values: List[int] = []
    while value > 0 or not values:
        remainder = value % base
        values.append(remainder)
        value //= base
    values.reverse()
    return ''.join(translate(v) for v in values)
