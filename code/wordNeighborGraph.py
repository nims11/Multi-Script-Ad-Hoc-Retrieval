from wordDictLinear import WordApproxDictionary
class WordNeighborGraphNode:
    def __init__(self, wordNode):
        self.word = wordNode
        self.left = WordApproxDictionary()
        self.right = WordApproxDictionary()
