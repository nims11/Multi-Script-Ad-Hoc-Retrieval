#!/bin/python
import sys 
from common import *
ngramLimitX = xrange(2, 4)
ngramLimitY = xrange(1, 4)
resultDict = {}
dp = {}
def compute(st1, st2):
    global dp
    if st1 in dp:
        if st2 in dp[st1]:
            return dp[st1][st2]
    else:
        dp[st1] = {}
    if (st1 < len(currentX) and currentX[st1] != '$') and st2 < len(currentY):
        flag = False
        global resultDict
        if currentX[st1] == '^':
            compute(st1+1, st2)
        for ngramX in ngramLimitX:
            for ngramY in ngramLimitY:
                if compute(st1+ngramX, st2+ngramY):
                    xsub, ysub = currentX[st1:st1+ngramX], currentY[st2:st2+ngramY]
                    if xsub not in resultDict:
                        resultDict[xsub] = {ysub: 1}
                    else:
                        if ysub not in resultDict[xsub]:
                            resultDict[xsub][ysub] = 1
                        else:
                            resultDict[xsub][ysub] += 1
                    flag = True
        dp[st1][st2] = flag
        return flag 
    elif (st1 == len(currentX) or (st1 == len(currentX)-1 and currentX[st1] == '$')) and st2 == len(currentY):
        dp[st1][st2] = True
        return True
    else:
        dp[st1][st2] = False
        return False

if __name__ == '__main__':
    global currentX, currentY
    if len(sys.argv) != 3:
        print 'arguments: input output'
        sys.exit(1)
    text = open(sys.argv[1]).readlines()
    total = len(text)
    cur = 1
    for line in text:
        dp = {}
        currentX, currentY = line.decode('utf-8').split()
        currentX = '^'+currentX+'$'
        compute(0, 0)
        sys.stdout.write("\r%.1f%%" % (100.0*cur/total))
        sys.stdout.flush()
        cur += 1
    save_obj(resultDict, sys.argv[2])
