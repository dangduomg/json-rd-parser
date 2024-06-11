from .token import *
from .lexer import *
from .syntax_error import *


class Parser:
    def __init__(self, string: str, /):
        self._tokens = list(lexer(string))
        self._i = 0
        
    def parse(self, /) -> object:
        # start: value EOF
        res = self._value()
        self._expect('EOF')
        return res
        
    def _value(self, /) -> object:
        # value: LBRACE object_rest
        #      | LBRACK array_rest
        #      | primitive
        if self._curr_token.type == 'LBRACE':
            self._advance()
            return self._object_rest()
        elif self._curr_token.type == 'LBRACK':
            self._advance()
            return self._array_rest()
        else:
            return self._primitive()
        
    def _object_rest(self, /) -> dict:
        # object_rest: (pair (COMMA pair)*)? RBRACE
        res = {}
        if self._curr_token.type != 'RBRACE':
            k, v = self._pair()
            res[k] = v
            while self._curr_token.type == 'COMMA':
                self._advance()
                k, v = self._pair()
                res[k] = v
        self._expect('RBRACE')
        self._advance()
        return res
        
    def _pair(self, /) -> tuple[str, object]:
        # pair: STRING COLON value
        self._expect('STRING')
        k = str(self._curr_token.object)
        self._advance()
        self._expect('COLON')
        self._advance()
        v = self._value()
        return k, v
    
    def _array_rest(self, /) -> list:
        # array_rest: (value (COMMA value)*)? RBRACK
        res = []
        # value never starts with RBRACK
        if self._curr_token.type != 'RBRACK':
            res.append(self._value())
            while self._curr_token.type == 'COMMA':
                self._advance()
                res.append(self._value())
        self._expect('RBRACK')
        self._advance()
        return res
    
    def _primitive(self, /) -> object:
        # primitive: STRING
        #          | NUMBER
        #          | TRUE
        #          | FALSE
        #          | NULL
        self._expect('STRING', 'NUMBER', 'TRUE', 'FALSE', 'NULL')
        res = self._curr_token.object
        self._advance()
        return res
        
    @property
    def _curr_token(self, /) -> Token:
        return self._tokens[self._i]
    
    def _expect(self, /, *types: str) -> None:
        curr = self._curr_token
        if curr.type not in types:
            types_string = types[0] if len(types) == 1 else f'any of {types}'
            syntax_error(curr.line, curr.col, f'Expect {types_string}, got {curr.type}')
    
    def _advance(self, /) -> None:
        self._i += 1


def parse(s: str, /) -> object:
    return Parser(s).parse()