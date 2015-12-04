#!/usr/bin/python
import sys
from common import *

dp = [[0 for i in range(50)] for j in range(50)]
def LCS(w1, w2):
    for i in range(len(w1)+1):
        dp[i][0] = 0
    for i in range(len(w2)+1):
        dp[0][i] = 0
    for i in range(1, len(w1)+1):
        for j in range(1, len(w2)+1):
            dp[i][j] = max(dp[i-1][j], dp[i][j-1])
            if w1[i-1] == w2[j-1]:
                dp[i][j] = max(dp[i][j], dp[i-1][j-1]+1)
    return dp[len(w1)][len(w2)]

def getSimilarity(word, targetWord):
    word = toUnicode(word)
    targetWord = toUnicode(targetWord)
    return LCS(word, targetWord)/float(max(len(targetWord), len(word)))
