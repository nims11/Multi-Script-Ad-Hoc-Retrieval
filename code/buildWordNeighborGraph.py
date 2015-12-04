import sys, os, re, shelve, random
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from wordNeighborGraph import WordNeighborGraphNode
from wordDictLinear import WordApproxDictionary
from collections import defaultdict
from common import *
outfname = '../data/fire_graph/graph'
outglobalname = '../data/global_dict.dat'
documents_list = sys.argv[1:]
words = load_obj('../data/fire_docs/idf_fire.dat')
globalDict = WordApproxDictionary()
first_let = set ()
outDict = {}
print 'Finished Initializing'
for word in words:
    globalDict.insert({'word': word, 'doc': None})
    first_let.add(hash(word[0])%20)

save_obj(globalDict, outglobalname)
class dictDisk:
    def __init__(self, alt=""):
        self.cacheDict = {}
        self.cacheSize = 30000
        self.globSet = set()
        self.prefix = alt

    def removeKey(self, key):
        if key in self.cacheDict:
            fname = os.path.join(outfname, str(hash(self.prefix+key))+'.dat')
            save_obj(self.cacheDict[key], fname)
            del self.cacheDict[key]

    def removeAll(self):
        for key in self.globSet:
            self.removeKey(key)
    
    def __getitem__(self, key):
        if key not in self.cacheDict:
            if len(self.cacheDict) == self.cacheSize:
                k2 = random.sample(self.cacheDict, 1)[0]
                self.removeKey(k2)
            if key in self.globSet:
                fname = os.path.join(outfname, str(hash(self.prefix+key))+'.dat')
                self.cacheDict[key] = load_obj(fname)
        return self.cacheDict[key]

    def __setitem__(self, key, value):
        self.globSet.add(key)
        if key not in self.cacheDict:
            if len(self.cacheDict) == self.cacheSize:
                k2 = random.sample(self.cacheDict, 1)[0]
                self.removeKey(k2)
        self.cacheDict[key] = value

for idx, first in enumerate(first_let):
    outDict = dictDisk()
    titleDict = dictDisk(alt="title")
    print idx
    for idx, documents in enumerate(documents_list):
        print idx, documents, len(outDict.globSet)
        docGroup = int(documents[documents.rfind('.')+1:])
        docGroup -= 1
        print 'Group:', docGroup
        documents = load_obj(documents)
        for idx, doc in enumerate(documents):
            idx = docGroup*1000 + idx
            # print idx, u' '.join(doc['title'])
            # content = cleanContent(doc['content'])
            # content = content.decode('utf-8')
            # content = filterWord(content)
            words = doc['content']
            title_words = doc['title']
            for i in range(len(words)):
                w = words[i]
                if hash(w[0])%20 != first:
                    continue
                if w not in outDict.globSet:
                    outDict[w] = WordNeighborGraphNode({'word': w, 'doc': defaultdict(int)})
                outDict[w].word['doc'][idx] += 1
                if i > 0:
                    outDict[w].left.insert({'word': words[i-1], 'doc': idx})
                if i < len(words) - 1:
                    outDict[w].right.insert({'word': words[i+1], 'doc': idx})
            for i in range(len(title_words)):
                w = title_words[i]
                if hash(w[0])%20 != first:
                    continue
                if w not in titleDict.globSet:
                    titleDict[w] = WordNeighborGraphNode({'word': w, 'doc': defaultdict(int)})
                titleDict[w].word['doc'][idx] += 1
                if i > 0:
                    titleDict[w].left.insert({'word': title_words[i-1], 'doc': idx})
                if i < len(title_words) - 1:
                    titleDict[w].right.insert({'word': title_words[i+1], 'doc': idx})
    outDict.removeAll()
    titleDict.removeAll()

