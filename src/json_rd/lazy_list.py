from typing import Iterator

class LazyList:
    def __init__(self, /, iterator: Iterator):
        self.iterator = iterator
        self._values = []
        
    def __getitem__(self, i: int, /) -> object:
        if i < 0:
            raise IndexError('LazyList index out of range')
        while len(self._values) <= i:
            try:
                self._values.append(next(self.iterator))
            except StopIteration:
                raise IndexError('LazyList index out of range')
        return self._values[i]