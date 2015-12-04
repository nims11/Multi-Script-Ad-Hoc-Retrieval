from collections import defaultdict
from Queue import Queue
class WordApproxDictionary:
    def __init__(self, relaxation):
        self.trie = {'words': [], 'edges': defaultdict(set)}
        self.relaxation = relaxation
    
    def query(self, word, threshold, numResults):
        """
        returns a list of (score, matched_word)
        state - (curNode, (matchedStr, remainingStr), (curSkip on word, totalSkip))
        Todo: fix bestPossibleScore
        """
        retDict = defaultdict(float)
        queue = Queue()
        wordLen = len(word)
        queue.put((self.trie, ('', word), (0, 0)))
        while not queue.empty():
            curNode, curWord, skipTuple = queue.get()
            skipWord, skips = skipTuple
            bestPossibleScore = wordLen/float(wordLen+skips)
            if bestPossibleScore < threshold:
                continue
            for word in curNode['words']:
                curNodeScore = len(word)/float(len(curWord[0]+curWord[1])+skips)
                if curNodeScore >= threshold:
                    retDict[word] = max(retDict[word], curNodeScore)
            nextTuple = (curWord[0] + curWord[1][0], curWord[1][1:])
            queue.put((curNode, nextTuple, skips+1))
            for relax, node in curNode['edges'][curWord[1][0]]:
                queue.put((node, nextTuple, skips + relax))

    def insert(self, word):
        curNode = self.trie
        cache = []
        for idx, char in enumerate(word):
            newNode = {'words': [], 'edges': defaultdict(set)}
            curNode['edges'][char].add((0, newNode))
            cache.append(curNode)
            for i in range(1, self.relaxation+1):
                if idx-i < 0:
                    break
                cache[idx-i]['edges'][word[idx-i]].add((i, newNode))
            curNode = newNode
        curNode['words'].append(word)
