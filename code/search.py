import sys, re, os
from similarityAnalyser import getSimilarity as editDistance
import build_model
from common import *
from collections import defaultdict
# documents = load_obj('../documents.dat')
# graph = load_obj('graph.dat')
globalDict = load_obj('../data/global_dict.dat')
globalDictTitle = globalDict['title']
globalDict = globalDict['content']
idf = load_obj('../data/fire_docs/idf_fire.dat')
# graph = graph['docGraph']
graphPath = '../data/fire_graph/graph'
idxToFile = load_obj('../data/idx_to_file.dat')
candidateTermsNum = 3
similarityThreshold = 0.7

intentWords = set()
for intentW in [u'lyric', u'lyrics', u'review', u'reviews', u'movie', u'movies', u'song', u'songs']:
    intentWords.add(build_model.transliterate(intentW)[0].decode('utf-8'))
# print 'Initialized..'
documents = []
for i in range(65):
    sys.stderr.write('loading document %d\n' % i)
    documents.append(load_obj('../data/fire_docs/documents_fire.dat.%d'%i))

def getTitle(idx):
    docid = idx // 1000
    docid += 1
    return set(documents[docid][idx%1000]['title'])

class dictDisk:
    def __init__(self, alt=""):
        self.cacheDict = {}
        self.cacheSize = 10000
        self.globSet = set()
        self.prefix = alt

    def removeKey(self, key):
        if key in self.cacheDict:
            # fname = os.path.join(outfname, str(hash(key))+'.dat')
            # save_obj(self.cacheDict[key], fname)
            del self.cacheDict[key]

    def removeAll(self):
        for key in self.globSet:
            self.removeKey(key)
    
    def __getitem__(self, key):
        if key not in self.cacheDict:
            if len(self.cacheDict) == self.cacheSize:
                k2 = random.sample(self.cacheDict, 1)[0]
                self.removeKey(k2)
            # if key in self.globSet:
            fname = os.path.join(graphPath, str(hash(self.prefix+key))+'.dat')
            self.cacheDict[key] = load_obj(fname)
        return self.cacheDict[key]

    # def __setitem__(self, key, value):
    #     self.globSet.add(key)
    #     if key not in self.cacheDict:
    #         if len(self.cacheDict) == self.cacheSize:
    #             k2 = random.sample(self.cacheDict, 1)[0]
    #             self.removeKey(k2)
    #     self.cacheDict[key] = value

graph = dictDisk()
titleGraph = dictDisk(alt="title")
def normCnt(cnt):
    cnt = min(2, minMaxNorm(cnt, 1, 4, 1, 2))
    return cnt
def expandLeft(node, curset, idx, query, nextDict=lambda x: x.left, incr=-1, globalDict=globalDict, graph=graph):
    if idx < 0 or idx >= len(query):
        return curset
    wordDict = nextDict(node)
    candidates = wordDict.query(query[idx], filterDoc=set(curset.keys()))
    ret = {}
    nextNodes = {}
    nextNodeDocs = set()
    for wordData, score in candidates:
        word, doc, cnt = wordData
        cnt = normCnt(cnt)
        if doc in curset:
            if word not in nextNodes:
                nextNodes[word] = {}
            cnt2 = min(cnt, curset[doc]['cnt'])
            nextNodes[word][doc] = {'range':idx, 'score':score+curset[doc]['score']*cnt2, 'cnt': cnt2}
            nextNodeDocs.add(doc)

    for doc in curset:
        if doc not in nextNodeDocs:
            ret[doc] = curset[doc]

    for w in nextNodes:
        tmpset = expandLeft(graph[w], nextNodes[w], idx+incr, query, nextDict, incr, globalDict=globalDict, graph=graph)
        for doc, ent in tmpset.items():
            if doc not in ret or ret[doc]['score'] < ent['score']:
                ret[doc] = ent

    return ret

def expandRight(node, curset, idx, query, globalDict=globalDict, graph=graph):
    return expandLeft(node, curset, idx, query, lambda x: x.right, 1, globalDict, graph)

def traverseGraph(node, score, idx, query, globalDict=globalDict, graph=graph):
    curset = {}
    idfVal = idf[node.word['word']]
    for doc, cnt in node.word['doc'].items():
        cnt = normCnt(cnt)
        curset[doc] = {'range': idx, 'score': score, 'cnt': cnt}
    leftRes = expandLeft(node, curset.copy(), idx-1, query, globalDict=globalDict, graph=graph)
    rightRes = expandRight(node, curset.copy(), idx+1, query, globalDict=globalDict, graph=graph)

    ret = {}
    for doc in set(leftRes.keys()+rightRes.keys()):
        if doc in leftRes and doc in rightRes:
            ret[doc] = {'rangeL': leftRes[doc]['range'], 
                    'rangeR': rightRes[doc]['range'],
                    'score': (leftRes[doc]['score']+rightRes[doc]['score']-score)*(rightRes[doc]['range']-leftRes[doc]['range']+1)}
        elif doc in leftRes:
            ret[doc] = leftRes[doc]
        else:
            ret[doc] = rightRes[doc]

    return ret

def selectAndExpand(queryWords, graph=graph, globalDict=globalDict):
    queryIdf = {}
    candidateWords = {}
    for w in queryWords:
        if w in candidateWords:
            continue
        candidateWords[w] = globalDict.query(w)
        for cdt, score in candidateWords[w]:
            cdt = cdt[0]
            if w not in queryIdf:
                queryIdf[w] = 0
            queryIdf[w] = max(queryIdf[w], idf[cdt])
    candidateStartWords = queryIdf.items()
    candidateStartWords.sort(key=lambda x: -x[1])
    maxIdf = candidateStartWords[0][1]
    candidateStartWords = dict(candidateStartWords[:candidateTermsNum])
    res = defaultdict(float)
    for idx, word in enumerate(queryWords):
        if word in candidateStartWords:
            localres = defaultdict(float)
            for w, score in candidateWords[word]:
                # if idf[w[0]] < maxIdf/3.5:
                #     continue
                tmpres = traverseGraph(graph[w[0]], score, idx, queryWords, globalDict, graph)
                for doc, v in tmpres.items():
                    localres[doc] = max(localres[doc], v['score'])
                if score > 0.95:
                    break
            for doc, v in localres.items():
                res[doc] += v
    return res


def queryDocs(query):
    """
    TD: Scheme for repeating words in the query
    returns: [(score, doc),...]
    """
    query = re.sub('[,.!?\-]', ' ', query)
    query = toUnicode(query)
    query = filterWord(query)
    queryWords = query.split()
    qtmp = []
    intent = []
    for w in queryWords:
        if w in intentWords:
            intent.append(w)
        else:
            qtmp.append(w)
    queryWords = qtmp
    
    res1 = selectAndExpand(queryWords, graph, globalDict)
    try:
        res2 = selectAndExpand(queryWords, titleGraph, globalDictTitle)
        for k, v in res2.items():
            res1[k] += v*1.5
    except Exception as e:
        pass

    for k, v in res1.items():
        title = getTitle(k)
        for inw in intent:
            for w in title:
                if editDistance(w, inw) >= 0.7:
                    res1[k] += 0.2
                    break

    res = res1.items()

    res.sort(key=lambda x: -x[1])
    for i in range(len(res)):
        # print res[i][0]
        res[i] = (idxToFile[res[i][0]], res[i][1])
    return res
# @profile
def transAndSearch(query):
    idx, query = query.split(query[2],1)
    query = cleanContent(query)
    sys.stderr.write(query+'\n')
    transQuery = []
    for q in query.split():
        res = build_model.transliterate(q)
        transQuery.append(res[0])
    transQuery = ' '.join(transQuery)
    sys.stderr.write(transQuery+'\n')
    res = queryDocs(transQuery)[:30]
    resDict = []
    resDict.append(transQuery)
    fireFinal = []
    rank = 1
    maxScore = 0
    for doc, score in res:
        resDict.append({'score': score, 'content': doc})
        fireFinal.append({'score': score, 'doc': doc, 'rank': rank})
        maxScore = max(maxScore, score)
        # print idx, 'Q0', doc, rank, score
        rank += 1
    for x in fireFinal:
        print idx, 'Q0', x['doc'], x['rank'], x['score']/float(maxScore)
    sys.stdout.flush()

if __name__ == '__main__':
    # query = sys.argv[1]
    with open(sys.argv[1]) as f:
        for line in f.read().decode("utf-8-sig").encode("utf-8").strip().splitlines():
            transAndSearch(line)

