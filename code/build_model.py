#!/usr/bin/python
import sys, os
from common import *
ngramLimitX = xrange(1, 4)
resultDict = load_obj('../data/transliterationModel.dat')
global modelMap, modelMapComplete
from similarityAnalyser import getSimilarity
modelMap = {}
modelMapComplete = {}
modelMapCompleteLimit = 8
modelMapCompleteThreshold = 0.10
scoreThreshold = 0.15
transDict = load_obj('../data/transDict.dat')

def getScore(word, freq, totalFreq):
    return freq/float(totalFreq)

for xWord, yWordDict in resultDict.items():
    maxFreq = max(yWordDict.items(), key=lambda x: x[1]*len(x[0]))
    totalFreq = reduce(lambda res, (x, y): res+y, yWordDict.items(), 0)
    modelMap[xWord] = (maxFreq[0], getScore(maxFreq[0], maxFreq[1], totalFreq))
    modelMap['^'] = modelMap['$'] = ('', 1)

    modelMapComplete['^'] = modelMapComplete['$'] = [('', 1)]
    tmpList = [(yWord, getScore(yWord, yWordFreq, totalFreq)) for yWord, yWordFreq in yWordDict.items()]
    tmpList.sort(key=lambda x: -x[1]*len(x[0]))
    modelMapComplete[xWord] = filter(lambda x: x >= modelMapCompleteThreshold, tmpList[:modelMapCompleteLimit//len(xWord)])

def compute(word):
    if len(word) == 0:
        return ('', 1)
    retAns = ('', 0)
    for ngramX in ngramLimitX:
        if ngramX <= len(word):
            subWord = word[:ngramX]
            if subWord in modelMap:
                repWord, repScore = modelMap[subWord]
                repScore *= ngramX
                remWord, remScore = compute(word[ngramX:])
                finalWord, finalScore = repWord+remWord, repScore*remScore
                if finalScore > retAns[1]:
                    retAns = (finalWord, finalScore)
    return retAns

def computeAll(word):
    if len(word) == 0:
        return dict([('', 1)])
    retAns = {}
    curngramlimitX = ngramLimitX
    for ngramX in curngramlimitX:
        if ngramX <= len(word):
            subWord = word[:ngramX]
            if subWord in modelMapComplete:
                resRest = computeAll(word[ngramX:]).items()
                for yWord, yWordScore in modelMapComplete[subWord]:
                    for remWord, remScore in resRest:
                        if remScore != 0:
                            finalAns, finalScore = yWord+remWord, yWordScore*remScore*ngramX*max(1, len(yWord))
                            if finalScore < scoreThreshold:
                                continue
                            if finalAns not in retAns:
                                retAns[finalAns] = 0
                            retAns[finalAns] = max(retAns[finalAns], finalScore)

    return retAns


def transliterate(word):
    if word in transDict:
        return list(transDict[word])[0], 1.0
    if isHindi(word):
        return word, 1.0
    word = word.lower()
    resWord, resScore = compute('^'+word+'$')
    finalWord = resWord.encode('utf-8')
    score = resScore
    if word in transDict:
        score = 0
        for w in transDict[word]:
            _score =  getSimilarity(w, resWord)
            if _score > score:
                score = _score
                finalWord = w
    return finalWord, score


def transliterateAll(word):
    resultLimit = 10
    res = computeAll('^'+word+'$').items()
    res.sort(key=lambda x: -x[1])
    return res[:resultLimit]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Argument: input output'
        sys.exit(1)
    with open(sys.argv[2]) as f:
        words = f.readlines()
    res = []
    for word in words:
        word = word.strip()
        resWord, resScore = compute(word)
        res.append(u'%s %s %f' % (word, resWord, resScore))
    with open(sys.argv[3], 'w') as f:
        f.write(u'\n'.join(res).encode('utf-8'))
