# Recursive descent json parser


from parser_ import *


def parse(s: str, /) -> object:
    return Parser(s).parse()