#!/usr/bin/env python
# -*- encoding: utf8 -*-

## @package tools
#@brief  This can translation between traditional and simplified chinese.
#@details  F2J: 繁轉簡 J2F: 簡轉繁.
#@authors Evan
#@version 1.0
#@date 2013-07-18

from charsets import gbk, big5

class _T(object):
    def __init__(self,dic):
        self.dic = dic

    def _decode(self,char):
        if type(char) is str:
            try:
                return char.decode('utf8')
            except:
                pass
        return char

    def get(self,text):
        text = self._decode(text)
        _check = lambda x: self.dic.get(x,x)
        return u''.join((_check(c) for c in text))

#簡轉繁
class J2F(_T):
    def __init__(self):
        super(J2F,self).__init__(dict(zip(gbk,big5)))

#繁轉簡
class F2J(_T):
    def __init__(self):
        super(F2J,self).__init__(dict(zip(big5,gbk)))

if __name__ == '__main__':
    print F2J().get('是太生氣了!!這是一隻烏龜不是鳥...')
