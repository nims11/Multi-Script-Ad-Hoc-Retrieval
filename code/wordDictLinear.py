from collections import defaultdict
from Queue import Queue
from similarityAnalyser import getSimilarity as editDistance
def intersect(s1, s2):
    ret = defaultdict(int)
    for k in s2:
        if k in s1:
            ret[k] += 1
    return ret
class WordDocData:
    def __init__(self):
        self.docSet = defaultdict(int)
    def add(self, doc):
        self.docSet[doc] += 1

class WordApproxDictionary:
    def __init__(self, relaxation=3):
        self.relaxation = relaxation
        self.words = defaultdict(WordDocData)
    
    def getSimilarity(self, w1, w2):
        """
        Todo: use relaxation
        """
        return editDistance(w1, w2)
    
    def query(self, word, threshold=0.7, numResults=20, filterDoc=None):
        """
        returns a list of (word, score, doc, count)
        """
        retDict = defaultdict(float)
        minLength = threshold*len(word) - 0.001
        maxLength = len(word)/threshold + 0.001

        for _word, wordData in self.words.items():
            _docset = wordData.docSet

            if len(_word) < minLength or len(_word) > maxLength:
                continue

            # if filterDoc != None:
            #     _finalDocSet = intersect(_docset, filterDoc)
            # else:
            #     _finalDocSet = _docset
            # if not _finalDocSet:
            #     continue

            score = self.getSimilarity(_word, word)
            if score >= threshold:
                for _doc, _cnt in _docset.items():
                    if filterDoc == None or _doc in filterDoc:
                # for _doc, _cnt in _finalDocSet.items():
                    #### Remove Max Here ####
                        retDict[(_word, _doc, _cnt)] = max(retDict[(_word, _doc, _cnt)], score)
        retList = retDict.items()
        retList.sort(key=lambda x: -x[-1])
        while numResults < len(retList) and retList[numResults][-1] >= 0.9:
            numResults += 1
        return retList[:numResults]

    def insert(self, wordNode):
        """
        WIP: same word across multiple documents optimize
        """
        self.words[wordNode['word']].add(wordNode['doc']);

if __name__ == '__main__':
    dictFile = '/usr/share/dict/cracklib-small'
    test = WordApproxDictionary()
    with open(dictFile) as f:
        for x in f.readlines():
            x = x[:-1]
            test.insert({'word': x, 'doc': None})
