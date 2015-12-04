from collections import defaultdict
import sys, os, math
from bs4 import BeautifulSoup
import HTMLParser
h = HTMLParser.HTMLParser()
from common import *
import build_model
docpath = sys.argv[1]
outdir = sys.argv[2]
idf = {}
documents = []
def processLine(line):
    contentWords = []
    for word in line.split():
        word = filterWord(word)
        if not isHindi(word) and not isDigits(word):
            word = word.lower()
            prevWord = word
            word = toUnicode(build_model.transliterate(word)[0])
            if len(word) == 0:
                word = prevWord
        if word == u'':
            continue
        contentWords.append(word)
    return contentWords

err = []
totalDoc = 0
curId = 0
docCount = defaultdict(int)
files = os.listdir(docpath)
# for f in os.listdir(os.path.dirname(docpath)):
#     f = os.path.join(os.path.dirname(docpath), f)
#     if f.find('documents_fire.dat') != -1:
#         print f
#         documents = load_obj(f)
#         totalDoc += len(documents)
#         for doc in documents:
#             for word in set(doc['content']+doc['title']):
#                 docCount[word] += 1

textRegex = re.compile(r'###(.*?)###', re.DOTALL+re.MULTILINE)

def unescapeHtml(content):
    content = h.unescape(content.replace('andamp;', '&').replace('andlt;', '<').replace('andgt;', '>').replace('<br />', ' '))
    return content;

def parseContent(content):
    content = content.replace('\r', '')
    soup = BeautifulSoup(content, 'lxml', from_encoding='utf-8')
    title = unescapeHtml(soup.find('title').text)
    body = unescapeHtml(soup.find('text').text)
    title, body = title.strip(), body.strip()
    if len(title) == 0:
        titleMatch = textRegex.match(body)
        if titleMatch != None:
            body = textRegex.sub('', body).strip()
            title = titleMatch.group(1).strip()
    return title, body

for idx, f in enumerate(files):
    f = os.path.join(docpath, f)
    print f, idx
    totalDoc += 1
    # if idx % 1000 == 0:
    #     if idx + 1000 < len(docpath):
    #         curId += 1
    #         documents = []
    #         continue
    # else:
    #     continue
    # print  curId, idx
    if idx % 1000 == 0:
        print 'Saving...'
        save_obj(documents, os.path.join(outdir, 'documents_fire.dat.%d' % curId))
        documents = []
        curId += 1
    with open(f) as cur_file:
        content = cur_file.read().decode('utf-8')
        title, body = parseContent(content)
        title, body = cleanContent(title), cleanContent(body)
        # print (body)
        finalTitle = []
        finalBody = []
        for line in title.splitlines():
            finalTitle += processLine(line)

        for line in body.splitlines():
            finalBody += processLine(line)
        # continue
        # lines = cur_file.read().encode('utf-8').splitlines()
        # title = ''
        # contentWords = []
        # titleWords = []
        # for idx, line in enumerate(lines):
        #     if len(line) > 0 and line[0] == '<':
        #         continue
        #     if title == '':
        #         if idx > 0 and len(lines[idx-1]) > 1:
        #             if lines[idx-1][1] == '#':
        #                 title = lines[idx]
        #     elif len(line) > 1 and line[1] != '#':
        #         line = cleanContent(line)
        #         contentWords += processLine(line)
        if len(finalTitle) == 0 and len(finalBody) == 0:
            print 'Error in doc', f
            sys.stderr.write(f+'\n')
            err.append(f)
        else:
            for word in set(finalBody+finalTitle):
                docCount[word] += 1
            documents.append({'content': finalBody, 'title': finalTitle, 'file': os.path.basename(f)})

print totalDoc, len(docCount)
for k, v in docCount.items():
    idf[k] = math.log(totalDoc/float(v))

save_obj(idf, os.path.join(outdir, 'idf_fire.dat'))
save_obj(documents, os.path.join(outdir, 'documents_fire.dat.%d' % curId))
documents = []
curId += 1
