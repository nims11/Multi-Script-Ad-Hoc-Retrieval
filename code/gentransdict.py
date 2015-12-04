from common import *
d = {}
with open('../transDict.txt') as f:
    for line in f.readlines():
        line = line[:-1]
        k, v = line.split()
        if k not in d:
            d[k] = set()
        d[k].add(v)

save_obj(d, '../data/transDict.dat')
