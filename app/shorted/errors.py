from enum import Enum


class ErrorCodes(Enum):
    INVALID_CONTENT_TYPE = 0
    INVALID_SCHEMA = 1
    INVALID_URL = 2
    NO_SUCH_SHORTCUT = 3
    CONFLICT = 4
