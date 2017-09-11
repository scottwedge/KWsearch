#!/usr/bin/env python
# -*- encoding: utf8 -*-

## @package tools
#@brief  Check word is alpa or numbers.
#@details  檢查字元字串是否純英文數字.
#@authors Evan
#@version 1.0
#@date 2013-04-24

import re
import sys
import optparse

def format(text):
    return text if type(text) == unicode else text.decode('utf8')

def tryPattern(pattern,text):
    if len(text) == 0: return False
    tmp = re.findall(pattern,text)
    if len(tmp) == len(text):
        return True
    else:
        return False

def isWDmix(text):
    text = format(text)
    return tryPattern('[a-zA-Z0-9]',text)

def isAlph(text):
    text = format(text)
    return tryPattern('[a-zA-Z]',text)

def isNum(text):
    text = format(text)
    return tryPattern('[0-9]',text)

#EZ Unitesting
if __name__ == '__main__':
    case_1, case_2, case_3 , case_4 = '1a', 'a', '3', '__'
    print 'mix :', isWDmix(case_4), case_4
    print 'alph :', isAlph(case_4), case_4
    print 'num :', isNum(case_4), case_4
    print 'mix :', isWDmix(case_1), case_1
    print 'alph :', isAlph(case_2), case_2
    print 'num :', isNum(case_3), case_3

