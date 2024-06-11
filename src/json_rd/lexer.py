import re
from typing import Iterator
from ast import literal_eval

from .token import *
from .syntax_error import *


PATTERNS = re.compile(r"""
      (?P<LBRACE>     {
    )|(?P<RBRACE>     }
    )|(?P<LBRACK>     \[
    )|(?P<RBRACK>     ]
    )|(?P<COLON>      :
    )|(?P<COMMA>      ,
    )|(?P<TRUE>       true
    )|(?P<FALSE>      false
    )|(?P<NULL>       null
    )|(?P<STRING>     " .*? (?:(?<!\\)"|$)
    )|(?P<NUMBER>     [+-]? \d+ (?:\.\d+)? (?:[Ee][+-]?\d+)?
    )|(?P<WS>         [ \t]+
    )|(?P<NL>         \n
    )|(?P<INVALID_ID> [A-Za-z_]\w*
    )|(?P<INVALID>    .
    )
""", re.X | re.M)

VALID_IDS = ('true', 'false', 'null')

UNBAL_RE = re.compile(r'(?<!(?<!\\)")$')
CTRL_CHAR_RE = re.compile(r'[\x00-\x1f]')
INVALID_ESC_RE = re.compile(r'\\(?:[^bfrntu"\\/]|u[\dA-Fa-f]{0,3}(?![\dA-Fa-f]))')


def lexer(s: str) -> Iterator[Token]:    
    line = 1
    line_start = 0
    
    for m in PATTERNS.finditer(s):
        type_ = str(m.lastgroup)
        lexeme = m[type_]
        object_: object = None
        col = m.start(type_) - line_start
        if type_ in ('TRUE', 'FALSE'):
            object_ = (type_ == 'TRUE')
        elif type_ == 'STRING':
            if unbal_match := UNBAL_RE.search(lexeme):
                col += unbal_match.start()
                syntax_error(line, col, 'Unbalanced string')
            if ctrl_char_match := CTRL_CHAR_RE.search(lexeme):
                col += ctrl_char_match.start()
                syntax_error(line, col, 'Control character found in string')
            if invalid_esc_match := INVALID_ESC_RE.search(lexeme):
                col += invalid_esc_match.start()
                syntax_error(line, col, 'Invalid escape sequence')
            object_ = literal_eval(lexeme)
        elif type_ == 'NUMBER':
            i = 0
            if lexeme[i] in ('+', '-'):
                i += 1
            if lexeme[i] == '0':
                i += 1
                if re.match(r'\d', lexeme[i]):
                    syntax_error(line, col, 'Leading zeros are disallowed')
            object_ = float(lexeme)
        elif type_ == 'WS':
            continue
        elif type_ == 'NL':
            line += 1
            line_start = m.start(type_) + 1
            continue
        elif type_ == 'INVALID_ID':
            syntax_error(line, col, f'Only allowed identifiers are {VALID_IDS}')
        elif type_ == 'INVALID':
            syntax_error(line, col, 'Invalid character')
        yield Token(type_, lexeme, object_, line, col)
        
    yield Token('EOF', '', None, line, len(s) - line_start)
