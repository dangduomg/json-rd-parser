from typing import NamedTuple


class Token(NamedTuple):
    type: str
    lexeme: str
    object: object
    line: int
    col: int
