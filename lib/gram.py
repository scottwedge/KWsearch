#!/usr/bin/env python
# -*- encoding: utf8 -*-

## @package tools
#@brief Split n grams, and mmseg method.
#@details 辨別中英文切段處理,v2.0新增MMSEG,v3.0新增Grams Vector,v4.0修改物件結構
#@authors Evan
#@version 4.2
#@date 2013-04-24
#@update 2013-08-27

import re
import os

import checkWords

def getUnicode(text):
    if type(text) is not unicode:
        try:
            return text.decode('utf8')
        except:
            pass
    return text

class Vector:
    #資料格式1 data = 'TEXT' (need gram)
    #資料格式2 data = ['A','B']
    #資料格式3 data = [['A','B'],[list],...]
    #資料格式4 data = [ (1,['A','B']), (n,[list]) ]
    def __init__(self,**options):
        self._mapping = options.get('dic',False)
        self._gram = options.get('gram',Gram())
        self.keys = set()
        self.__key_map = {}
        self.__val_map = {}

    def __countWithClass(self):
        tmp = []
        self.keys = set()
        try:
            for k,v in self._data:
                vec = self.__count(v)
                self.keys.update(vec.keys())
                tmp.append((k,vec))
        except:
            for v in self._data:
                vec = self.__count(v)
                self.keys.update(vec.keys())
                tmp.append(vec)

        if self._mapping:
            temp = []
            _map = lambda x,y: dict(zip(x,y))
            self.__key_map = _map(self.keys,range(len(self.keys)))
            self.__val_map = _map(range(len(self.keys)),self.keys)
            try:
                for k,v in tmp:
                    temp.append((k,dict([(self.__key_map[kk],vv) for kk,vv in v.items()])))
            except:
                for v in tmp:
                    temp.append(dict([(self.__key_map[kk],vv) for kk,vv in v.items()]))
            return temp
        return tmp

    def __count(self,data=None):
        _unit = 1
        vec = {}
        data = self._data if data is None else data
        for w in data:
            num = vec.get(w,0) + _unit
            vec[w] = num
        return vec

    #@return_1 <dict> [(0,{'a':1,'b':2}),(1,{...})...]
    #@return_2 <dict> [{'a':1,'b':2},{'c':3...}...]
    def get(self,data=''):
        if type(data) is not list:
            self._data = self._gram.get(data)
        else:
            self._data = data

        try:
            return self.__count()
        except:
            return self.__countWithClass()
        return None

    #Find key number by words
    def getWord2Key(self):
        return self.__key_map

    #Find words by key number
    def getKey2Word(self):
        return self.__val_map

#用向量表去切文章
class VectorGram:
    #@input_type (dic == <dict>/<set>, ngram == <Gram class obj>)
    def __init__(self,dic,ngram=None):
        if type(dic) is not dict and type(dic) is not set:
            print type(dic)
            raise Exception('Error Dict Type!')
        self._dic = dic
        self._vector = Vector()
        self._ngram = Gram() if ngram is None else ngram

    #@input <str>
    #@return ['a', 'b', ...]
    #@explan 僅切割包含在<dict>中的字詞
    def get(self,text):
        return [w for w in self._ngram.get(text) if w in self._dic]

    #@input <str>
    #@return {'a':1, 'b':2, ...}
    def getv(self,text):
        temp = self.get(text)
        return dict((s,temp.count(s)) for s in set(temp))

    #@input <str>
    #@return {DICT_ID:1, DICT_ID:2, ...}
    def getdv(self,text):
        temp = self._ngram.get(text)
        return self._vector.get(map(self._dic.get,temp))
        #若無法mapping或找無相關數據, 則會回傳None
        #若回傳None容易出錯, 建議pop(None, None)

class Gram:
    DEF_NUM = 2
    DEF_ALL = True
    DEF_EN = True
    #@input text == <<str>>, 
    #@input len == <int>, all == <bool>, en == <bool>, num == <bool>,
    #@input opts == <dict>
    def __init__(self,text=None,opts={},**options):
        if type(text) is dict:
            raise Exception('[Text Type Error]: %s' % text)
        if len(opts) > 0: options.update(opts)
        self.__text = ''
        self.__ngram = options.pop('len',2)
        self.__gramNum = options.pop('num',False)
        self.__gramAll = options.pop('all',True)
        self.__pick = options.pop('pick', False)
        self.__useEnglish = options.pop('en',True)
        self.__rexp = ['_']
        self.__textFormat(text)
        if len(options) > 0:
            raise Exception, options

    @staticmethod
    def help():
        join = lambda *x: '\t'.join(map(str,x))
        print join('len', Gram.DEF_NUM, '斷字長度')
        print join('all', Gram.DEF_ALL, '包括小於len所有斷字')
        print join('en', Gram.DEF_EN, '取英文字')
        print join('num', Gram.DEF_EN, '取數字')

    def __textFormat(self,text):
        if text is not None:
            self.__text = getUnicode(text)

    def addFilterWord(self,wd):
        self.__rexp.append(wd)

    #@ex 轉換格式為字串陣列
    def transformat(self,text=''):
        text = text if text != '' else self.__text
        text = getUnicode(text.lower())
        rexp = u'[^\u3400-\u9fa5\da-zA-Z]+'
        text = re.sub(rexp,' ',text).strip().lstrip()
        return text.split()

    def breakup(self,seg):
        if self.__gramNum:
            __en_pattern = '[a-zA-Z\d]'
        else:
            __en_pattern = '[a-zA-Z]'
            seg = re.sub('[\d]+','',seg)
        __startGram = 2 if self.__gramAll else self.__ngram
        tmp = []
        #"""
        #將文中的英文單字挑出
        tmp = re.findall('%s{2,}' % __en_pattern,seg) if self.__useEnglish else []
        #將文中的英文單字刪除
        seg = re.sub('%s{2,}' % __en_pattern,'',seg)
        #"""
        #1Gram Process
        if self.__gramAll or self.__ngram == 1:
            for s in re.sub(__en_pattern,'',seg):
                tmp.append(s)

        gramlimit = self.__ngram + 1
        gramrange = self.__ngram - 1
        for n in xrange(__startGram,gramlimit):
            for i in xrange(len(seg)-gramrange):
                tmp.append(seg[i:i+n])

        return tmp

    def gram(self,filteredWD):
        __lowbound = 1
        __gram = []
        for seg in filteredWD:
            slen = len(seg)
            if checkWords.isNum(seg) and slen > 1:
                if self.__gramNum: __gram.append(seg)
            elif checkWords.isWDmix(seg) and slen > __lowbound:
                if self.__useEnglish : __gram.append(seg)
                else: continue
            elif self.__pick and slen == 1:
                _seg = re.match('[^a-zA-Z\d]', seg)
                if _seg: __gram.append(seg)
            elif slen > 0:
                __gram.extend(self.breakup(seg))

        return __gram

    #@input <str>
    def get(self,text=None):
        return self.gram(self.transformat(text))

    def seg(self,text):
        content = self.transformat(text)
        return (self.gram((l,)) for l in content if len(l) >= self.__ngram)

    def setGramNumber(self,n):
        if n > 0: self.__ngram = n

    def setGramAll(self,v=True):
        self.__gramAll = v

    def setEnglish(self,v=True):
        self.__useEnglish = v

class MMseg:
    _DIR_PATH = 'data/dic'
    _TEMP_DICT = '%s/temp.dic' % _DIR_PATH
    #@input <str>dict_path
    #@ex load dictionary first
    def __init__(self,dic_path='%s/%s' % (
        os.path.dirname(__file__),_DIR_PATH),opts={},**options):
        if len(opts) > 0: options.update(opts)
        self.__useNumbers = options.pop('num',False)
        self.__useEnglish = options.pop('en',True)
        self.__standard = options.pop('std',False)
        self.__segall = options.pop('all',self.__standard)
        self.__mixseg = options.pop('mix',False)
        self.__max_length_limit = options.pop('limit',-1)
        self.__dic = {}
        if len(options) > 0: raise Exception,options

        if isinstance(dic_path, dict):
            self.__load(dic_path)
        else:
            self.addDict(dic_path)

    def __load(self, dicts):
        self.__dic.update(dicts)

    def __loadDict(self,_dic_path):
        dic = []
        f = open(_dic_path,'r')
        text = f.read()
        text = re.sub('[\r ]+','',text)
        text = getUnicode(text)

        f.close()
        for l in text.split('\n'):
            if l == '': continue
            if self.__max_length_limit > 0 and len(l) > self.__max_length_limit: continue
            dic.append((l,None))
        self.__dic.update(dict(dic))
        return

    #INFO: 新增字典, 或增加字典路徑 (無更改動作)
    def addDict(self, dic_path):
        if not os.path.exists(dic_path): dic_path = self._DIR_PATH
        if os.path.isdir(dic_path):
            path = lambda x: '%s/%s' % (re.sub('/$','',dic_path),x)
            map(self.__loadDict,map(path,os.listdir(dic_path)))
        else:
            self.__loadDict(dic_path)

    #@input_1: type(seg) == str
    #@input_2: type(seg) == list
    #@Warning: 如果seg只有一筆請勿使用list作為input
    def dict_update(self,seg,temp_path=''):
        if type(seg) is list:
            seg = map(getUnicode, seg)
        else:
            seg = getUnicode(seg)

        if temp_path == '': temp_path = self._TEMP_DICT
        dic = []
        if not os.path.exists(temp_path):
            kwset = set()
        else:
            with open(temp_path) as f:
                kwset = set(f.read().split('\n')) - set(['',' '])
        ifin = lambda x: x not in self.__dic and x not in kwset

        if type(seg) is not list:
            seg = Gram(opts={'all':False,'en':False}).transformat(seg)

        dic = [(s,None) for s in filter(ifin,seg)]
        if len(dic) < 1: return False
        for s in seg: kwset.add(s.encode('utf8'))

        temp = '\n'.join(kwset)
        self.__dic.update(dict(dic))
        with open(temp_path,'w') as f:
            f.write(temp)
        return True

    #INFO: 判斷單詞是否在字典內
    def check(self,s):
        return getUnicode(s) in self.__dic

    def __fastBreak(self,seg,reverse=False):
        lowbound = 1
        temp_gram = []
        slen = len(seg)
        if slen == lowbound:
            return seg if self.__segall else ''
        for n in xrange(slen):
            if not reverse:
                temp = seg[n:]
            else:
                temp = seg[:-n] if n > 0 else seg
            if len(temp) == lowbound:
                if self.__segall: temp_gram.append(temp)
                if not reverse:
                    temp_gram.extend(self.__fastBreak(seg[:n],reverse))
                else:
                    temp_gram.extend(self.__fastBreak(seg[-n:],reverse))
                return temp_gram
            elif temp in self.__dic or (self.__useEnglish and checkWords.isAlph(temp)):
                if not reverse:
                    lastseg = seg[:n]
                else:
                    lastseg = seg[-n:] if n > 0 else ''
                temp_gram.append(temp)
                temp_gram.extend(self.__fastBreak(lastseg,reverse))
                return temp_gram
        return temp_gram

    def __seg(self,content):
        __lowbound = 1
        __gram = []
        for seg in content:
            seg = seg.lower()
            slen = len(seg)
            if (not self.__useNumbers) and checkWords.isNum(seg):
                continue
            elif checkWords.isWDmix(seg) and slen > __lowbound:
                if self.__useEnglish : __gram.append(seg)
                else: continue
            elif slen > 0:
                self.gram.setGramAll(False)
                seg = re.sub('[\d]+','',seg)
                if self.__standard:
                    #由後往前挑字
                    __gram.extend(reversed(self.__fastBreak(seg)))
                elif self.__mixseg:
                    count = 0
                    __gram.extend(
                        set(self.__fastBreak(seg,reverse=True)) |
                        set(reversed(self.__fastBreak(seg)))
                    )
                else:
                    #由前往後挑字
                    __gram.extend(self.__fastBreak(seg,reverse=True))

        return __gram


    def get(self,text): #標準取字
        self.gram = Gram()
        content = self.gram.transformat(text)
        return self.__seg(content)

    def seg(self,text): #斷句再斷字
        self.gram = Gram()
        content = self.gram.transformat(text)
        return [self.__seg((l,)) for l in content if l != '']

    def getDict(self): #取得字典所有關鍵字
        return self.__dic.keys()

    def setWantNumbers(self,v=True): #預設不取數字
        self.__useNumbers = v

    def setEnglish(self,v=True): #預設有英文斷詞
        self.__useEnglish = v

    def setDiscrete(self,v=True): #同setSegAll()
        self.setSegAll(v)

    def setSegAll(self,v=True): #無預設: 二元以下無論取樣
        self.__segall = v

    def setStandard(self,v=True): #無預設: 類似完整句子切斷輸出
        self.__discrete = self.__standard = v

    def setMixseg(self,v=True): #無預設: 先取字典再取ngram
        self.__mixseg = v

    def setBlock(self,path): #黑名單字典
        if not os.path.exists(path):
            raise Exception, 'Not Exists: %s' % path
        content = open(path,'r').read()
        block = re.sub(u'[\r ]+','', getUnicode(content))
        block = block.split('\n')
        pop = lambda x: self.__dic.pop(x,None)
        map(pop,block)

#unitest exapmple
if __name__ == '__main__':
    text = (
        'Hello World!哈囉你好!\n'
        "'“','”','，','。','！','？','；','：','「','」','《','》','（','）','、','〔','〕','※','＠',"
        '我愛T恤也愛HTC~~\n嗎\n'
        '前6個月4.99%、第7個月後定儲ABC指數+5%(目前定D儲EF指數為0.93%)=5.93%\[]'
        '天下為公, 一言為定, 害人不淺, 很好吃, 龖, 白蘭氏'
    )
    text1 = (
        '過去,不乏商業人士或政客利用假期到歐美的野雞學校"進修"學位，'
        '以至於有一位在學歷欄填寫某大學博士的立委候選人被他的對手挑戰說，'
        '只要他能提出初中以上任何學歷證明，變願意承認他的博士學位,到歐美的野雞學校'
    )
    g = Gram(opts={'all':False})
    import colors,time
    print colors.green('grams:')
    st = time.time()
    print ','.join(g.get(text))
    print time.time() -st
    print colors.green('mmseg:')
    m = MMseg()
    st = time.time()
    #print ','.join([ wd for wd in  m.get(text)])
    #m.setDiscrete() #以字典內優先,剩下取1-2grams
    m.setStandard() #標準mmseg效率約為2000kb/s ~ 4000kb/s
    print 'Standard:'
    print ','.join([ wd for wd in m.get(text)])
    m.setStandard(False) #標準mmseg效率約為2000kb/s ~ 4000kb/s
    print 'Mixseg:'
    m.setMixseg() #mix mmseg效率約為1500kb/s ~ 3000kb/s
    print ','.join([ wd for wd in m.get(text)])
    print m.seg(text1)
    print time.time() -st
    print colors.green('vector:')
    st = time.time()
    v = Vector(dic=True)
    print v.get([(0,m.get(text))])
    print time.time() -st
