import re
from typing import NamedTuple, Iterator

from .token_ import *
from .syntax_error import *


def lexer(s: str) -> Iterator[Token]:
    patterns = r"""
       (?P<LBRACE>  {
     )|(?P<RBRACE>  }
     )|(?P<LBRACK>  \[
     )|(?P<RBRACK>  ]
     )|(?P<COLON>   :
     )|(?P<COMMA>   ,
     )|(?P<TRUE>    true
     )|(?P<FALSE>   false
     )|(?P<NULL>    null
     )|(?P<STRING>  " .*? (?:(?<!\\)"|$)
     )|(?P<NUMBER>  [+-]? \d+ (?:\.\d+)? (?:e[+-]?\d+)?
     )|(?P<WS>      [^\n\S]+
     )|(?P<NL>      \n
     )|(?P<INVALID> .
     )
    """
    line = 1
    line_start = 0
    for m in re.finditer(patterns, s, re.X | re.I | re.M):
        type_ = str(m.lastgroup)
        lexeme = m[type_]
        object_: object = None
        col = m.start(type_) - line_start
        if type_ in ('TRUE', 'FALSE'):
            object_ = bool(lexeme)
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
                    if esc in ('"', '\\', '/'):
                        str_builder.append(esc)
                        i += 1
                    elif esc == 'b':
                        str_builder.append('\b')
                        i += 1
                    elif esc == 'f':
                        str_builder.append('\f')
                        i += 1
                    elif esc == 'r':
                        str_builder.append('\r')
                        i += 1
                    elif esc == 'n':
                        str_builder.append('\n')
                        i += 1
                    elif esc == 't':
                        str_builder.append('\t')
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
        elif type_ == 'INVALID':
            syntax_error(line, col, 'Invalid character')
        yield Token(type_, lexeme, object_, line, col)
