import pickle, re, traceback
import unicodedata as ud
def save_obj(obj, name ):
    with open(name, 'wb') as f:
        pickle.dump(obj, f, 
pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name, 'r') as f:
        return pickle.load(f)

def toUnicode(w):
    if type(w) != type(u''):
        w = unicode(w, 'utf8')
    return w

def cleanContent(content):
    return re.sub('[.]', '', re.sub(r'[\-#!$%^&*()_+|~=`{}\[\]:";'+"'"+'<>?,.\/]', ' ', content)).strip()

def filterWord(word):
    word = toUnicode(word)
    return word.replace(u'\u095b', u'\u091c\u093c')

def isHindi(word):
    word = toUnicode(word)
    for x in word:
        try:
            if 'DEVANAGARI' not in ud.name(x): return False
        except Exception as e:
            print traceback.format_exc()
            print word, x
            raise e
        return True

def isDigits(word):
    if len(word) == 0:
        return False
    return (ord('0') <= ord(word[0]) <= ord('9'))

def minMaxNorm(val, curmin, curmax, newmin, newmax):
    return (val-curmin)/(curmax-curmin)*(newmax-newmin) + newmin
