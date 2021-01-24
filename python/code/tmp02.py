import itertools

def chain(*iterables):
    for it in iterables:
        yield from it
if __name__=='__main__':
    a = 'ABC'
    t = tuple(range(3))
    print(list(chain(a, t)))