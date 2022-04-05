from itertools import zip_longest


def grouper(iterable:list, n:int, fillvalue:str=None):
    "Collect data into non-overlapping fixed-length chunks or blocks"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue = fillvalue)
