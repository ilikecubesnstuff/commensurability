from itertools import islice


def clump(iterable, size=10):
    while True:
        c = tuple(islice(iterable, size))
        if not c:
            return
        yield c