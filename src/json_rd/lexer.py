import re
from typing import Iterator

from .token import *
from .syntax_error import *


PATTERNS = r"""
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
"""
VALID_IDS = ('true', 'false', 'null')
LITERAL_ESCAPES = ('\\', '"', '/')
SPECIAL_ESCAPES = {
    'b': '\b',
    'f': '\f',
    'r': '\r',
    'n': '\n',
    't': '\t',
}


def lexer(s: str) -> Iterator[Token]:    
    line = 1
    line_start = 0
    for m in re.finditer(PATTERNS, s, re.X | re.M):
        type_ = str(m.lastgroup)
        lexeme = m[type_]
        object_: object = None
        col = m.start(type_) - line_start
        if type_ in ('TRUE', 'FALSE'):
            object_ = type_ == 'TRUE'
        elif type_ == 'STRING':
            str_builder = []
            i = 1
            while True:
                if i >= len(lexeme):
                    syntax_error(line, col, 'Unbalanced string')
                c = lexeme[i]
                if c == '\\':
                    i += 1
                    if i >= len(lexeme):
                        col += i - 1
                        syntax_error(line, col, 'Unescaped backslash at the end of string')
                    esc = lexeme[i]
                    if esc in LITERAL_ESCAPES:
                        str_builder.append(esc)
                        i += 1
                    elif esc in SPECIAL_ESCAPES:
                        str_builder.append(SPECIAL_ESCAPES[esc])
                        i += 1
                    elif esc == 'u':
                        i += 1
                        codepoint = []
                        for j in range(4):
                            if i >= len(lexeme):
                                col += i - 1
                                syntax_error(line, col, 'Unicode escape incomplete')
                            c = lexeme[i]
                            if not re.match(r'[\da-f]', c, re.I):
                                col += i
                                syntax_error(line, col, 'Invalid character for Unicode escape')
                            codepoint.append(c)
                            i += 1
                        char = chr(int(''.join(codepoint), base=16))
                        str_builder.append(char)
                    else:
                        col += i
                        syntax_error(line, col, 'Invalid escape character')
                elif c == '"':
                    object_ = ''.join(str_builder)
                    break
                elif ord(c) < 0x20 or 0x80 <= ord(c) < 0xa0:
                    col += i
                    syntax_error(line, col, 'Unescaped control character')
                else:
                    str_builder.append(c)
                    i += 1
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
