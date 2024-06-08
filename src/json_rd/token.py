from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    type: str
    lexeme: str
    object: object
    line: int
    col: int
