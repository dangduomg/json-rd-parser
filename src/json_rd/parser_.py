from .token_ import *
from .lexer import *
from .syntax_error import *

class Parser:
    def __init__(self, string: str):
        self._tokens = list(lexer(string))
        self._i = 0
        
    def parse(self) -> object:
        # start: value EOF
        res = self._value()
        self._expect('EOF')
        return res
        
    def _value(self, /) -> object:
        # value: object
        #      | array
        #      | primitive
        # object always start with LBRACE
        if self._curr_token.type == 'LBRACE':
            return self._object()
        # array always start with LBRACK
        elif self._curr_token.type == 'LBRACK':
            return self._array()
        else:
            return self._primitive()
        
    def _object(self, /) -> dict:
        # object: LBRACE (pair (COMMA pair)*)? RBRACE
        self._expect('LBRACE')
        self._advance()
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
    
    def _array(self, /) -> list:
        # array: LBRACK (value (COMMA value)*)? RBRACK
        self._expect('LBRACK')
        self._advance()
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
        if self._is_end():
            if self._tokens:
                prev_token = self._tokens[self._i - 1]
                line = prev_token.line
                col = prev_token.col + len(prev_token.lexeme)
            else:
                line = 1
                col = 0
            return Token('EOF', '', None, line, col)
        return self._tokens[self._i]
    
    def _expect(self, /, *types: str) -> None:
        curr = self._curr_token
        if curr.type not in types:
            types_string = types[0] if len(types) == 1 else f'any of {types}'
            syntax_error(curr.line, curr.col, f'Expect {types_string}, got {curr.type}')
    
    def _advance(self, /) -> None:
        self._i += 1
        
    def _is_end(self, /) -> bool:
        return self._i >= len(self._tokens)


def parse(s: str, /) -> object:
    return Parser(s).parse()