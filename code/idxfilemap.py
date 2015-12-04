import sys, os
from common import *
docGroups = sys.argv[1:]
outfname = '../data/idx_to_file.dat'
resDict = {}
for idx, documents in enumerate(docGroups):
    print idx, documents
    docGroup = int(documents[documents.rfind('.')+1:])
    docGroup -= 1
    print 'Group:', docGroup
    documents = load_obj(documents)
    for idx, doc in enumerate(documents):
        idx = docGroup*1000 + idx
        resDict[idx] = doc['file']

save_obj(resDict, outfname)
