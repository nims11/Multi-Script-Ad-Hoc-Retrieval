#!/usr/bin/python
import sys, os, collections
import common
import math
import unicodedata as ud
totalDocs = 0
docFreq = collections.defaultdict(lambda: 0)
finalStruc = {}
def refineHindWord(word):
    word = word.decode('utf-8')
    return u''.join(filter(lambda x: 'DEVANAGARI' in ud.name(x), word)).encode('utf-8')


def calcTF(content):
    content2 = list(content.decode('utf8'))
    content = u''
    for idx, char in enumerate(content2):
        if char in ('\r', '\n'):
            char = u' '
        if 'DEVANAGARI' not in ud.name(char):
            content += u' '
        else:
            content += char

    totWords = 0
    ret = collections.defaultdict(lambda: 0)
    for word in content.split():
        ret[word.strip()] += 1
        totWords += 1
    for k in ret.keys():
        ret[k] = ret[k]/float(totWords)
    return dict(ret)

def calc(directory, outFile):
    global finalStruc, totalDocs
    finalStruc['documents'] = []
    finalStruc['idf'] = {}
    for root, _, files in os.walk(directory):
        for f, cur in zip(files, range(1, len(files)+1)):
            print '\r%d/%d' % (cur, len(files)),
            fullpath = os.path.join(root, f)
            totalDocs += 1
            docStruc = common.load_obj(fullpath)
            docStruc['TF'] = calcTF(docStruc['content'])
            for word in docStruc['TF'].keys():
                docFreq[word] += 1
            finalStruc['documents'].append(docStruc)
    for word, freq in docFreq.items():
        finalStruc['idf'][word] = math.log(float(totalDocs)/freq)

    common.save_obj(finalStruc, outFile)

if __name__ == '__main__':
    dname = sys.argv[1]
    outFile = sys.argv[2]
    calc(dname, outFile)
