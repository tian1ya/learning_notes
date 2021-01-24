import random
from functools import reduce, partial
from operator import mul, itemgetter
from random import shuffle
import collections
import re
import reprlib

RE_WORLD = re.compile("\w+")

class Sentence:
    def __init__(self, text):
        self.text = text

    def __iter__(self):
        return (word.groups() for word in RE_WORLD.finditer(self.text))

    def __repr__(self):
        return "sentence(%s)" % reprlib.repr(self.text)

def gen_AB():
    yield "A"
    print("a")
    yield "B"
    print("b")
    yield "C"
    print("c")

def artiprog_gen(begin, step, end=None):
    result = type(begin + step)(begin)
    forever = end is not None
    index = 0
    while forever and result <= end:
        yield result
        index += 1
        result = begin + index * step

if __name__=='__main__':
    # s = Sentence('"The time has come, " the walrus said,')
    # for word in s:
    #     print(word)

    # res = [x*3 for x in gen_AB()]

    # for i in res:
    #     print(i)
    aaa = artiprog_gen(0, 2, 10)
    for it in aaa:
        print(it)


