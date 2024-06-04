from typing import NoReturn

def syntax_error(line: int, col: int, msg: str) -> NoReturn:
    raise ValueError(f'Syntax error at line {line}, column {col}: {msg}')