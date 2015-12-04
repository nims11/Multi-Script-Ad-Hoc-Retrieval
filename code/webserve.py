#!/usr/bin/python
import web, build_model
from search import queryDocs, globalDict
import json
from common import *
urls = (
        '/', 'index',
        '/all', 'allTrans',
        '/search', 'search'
)

class index:
    def GET(self):
        render = web.template.render('./')
        return render.index()
    def POST(self):
        query = web.input().query
        retRes = []
        retScore = []
        for q in query.split():
            res, score = build_model.transliterate(q)
            retRes.append(res.decode('utf-8')), retScore.append(str(score))
        return u'%s<br />%s<br />%s' % (query, ' '.join(retRes), ' '.join(retScore))

class allTrans:
    def GET(self):
        render = web.template.render('./')
        return render.transAll()
    def POST(self):
        query = web.input().query
        retRes = []
        for q in query.split():
            res = build_model.transliterateAll(q)
            retRes.append(res)
        response = u''
        for res, q in zip(retRes, query.split()):
            response += u'<b>Transliteration for %s</b><br />' % q
            for word, score in res:
                response += u'%s  -  %s<br />' % (word, str(score))
            response += u'<hr />'
        return response

def getDocumentFromIdx(idx):
    # idx = int(idx[7:-4])
    # print idx
    # docid = idx // 1000
    # docid += 1
    # documents = load_obj('../data/fire_docs/documents_fire.dat.%d'%docid)
    # doc = documents[idx % 1000]
    content = '<h3>'+idx+'</h3>'
    with open('../documents/FinalDataSet_MS/'+idx) as f:
        content += '<pre>'+f.read()+'</pre>'
    return content
class search:
    def GET(self):
        render = web.template.render('./')
        return render.search()
    def POST(self):
        query = web.input().query
        query = cleanContent(query)
        print query
        transQuery = []
        for q in query.split():
            res = build_model.transliterate(q)
            transQuery.append(res[0])
            # res = build_model.transliterateAll(q)[:3]
            # prescore = 0
            # finalWord = res[0][0]
            # for w, _ in res:
            #     print w
            #     print globalDict.query(w)
            #     for _foo in globalDict.query(w):
            #         dicword, score = _foo
            #         if score > prescore:
            #             prescore = score
            #             finalWord = dicword[0]
            #     print finalWord
            # transQuery.append(finalWord)
        transQuery = ' '.join(transQuery)
        print transQuery
        res = queryDocs(transQuery)[:10]
        resDict = []
        resDict.append(transQuery)
        for doc, score in res:
            resDict.append({'score': score, 'content': getDocumentFromIdx(doc)})
        return json.dumps(resDict)

if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()
