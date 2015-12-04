import sys
def transAndSearch(query):
    print repr(query)
    idx, query = query.split(query[2],1)
    sys.stderr.write(query+'\n')
if __name__ == '__main__':
    # query = sys.argv[1]
    with open(sys.argv[1]) as f:
        for line in f.read().decode("utf-8-sig").encode("utf-8").strip().splitlines():
            transAndSearch(line)
