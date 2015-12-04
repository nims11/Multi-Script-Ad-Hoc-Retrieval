import sys, os, re, shelve, random
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from wordNeighborGraph import WordNeighborGraphNode
from wordDictLinear import WordApproxDictionary
from collections import defaultdict
from common import *
documents_list = sys.argv[1:]
idfFileName = '../data/fire_docs/idf_fire.dat'
outglobalname = '../data/global_dict.dat'
print 'Finished Initializing'
idf = {}
docCount = defaultdict(int)
totalDoc = 0
globalDict = {'title': WordApproxDictionary(), 'content': WordApproxDictionary()}
for idx, documents in enumerate(documents_list):
    print idx, documents
    documents = load_obj(documents)
    for idx, doc in enumerate(documents):
        totalDoc += 1
        words = doc['content'] + doc['title']
        for w in set(words):
            docCount[w] += 1
        for w in set(doc['title']):
            globalDict['title'].insert({'word': w, 'doc': None})
        for w in set(doc['content']):
            globalDict['content'].insert({'word': w, 'doc': None})
import math
for k, v in docCount.items():
    idf[k] = math.log(totalDoc/float(v))

save_obj(idf, idfFileName)
save_obj(globalDict, outglobalname)
