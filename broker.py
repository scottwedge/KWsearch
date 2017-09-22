#!/usr/bin/env python
# -*- encoding: utf8 -*-
#Brief  Miner broker
#Created 2017-09-04 @Evan

#import os


import re
import time
import json
import argparse

from hashlib import sha1
from concurrent import futures

import grpc
import miner_pb2
import miner_pb2_grpc

import config
import error

from lib.gram import Gram
from lib.fanjan import F2J

f2j = F2J()
gram = Gram(opts={'num': True})

def resp(st, code=0, msg=None, **args):
    _data = {'code': '0'}

    if code > 0: _data['code'] = str(code)
    elif msg: _data['msg'] = str(msg)


    for k, v in args.items():
        _type = type(v)
        if _type is list or _type is dict:
            _temp = json.dumps(v)
        else: _temp = str(v)
        _data[k] = _temp

    _data['pt'] = str((time.time() - st) * 1000)
    return miner_pb2.Response(
        body=_data
    )

def genId(source):
    return sha1(''.join(map(str, source))).hexdigest()

def noNumWords(content):
    return re.search('[^0-9a-zA-Z_\-]+', content)

def checkAppid(func):
    def check(body, opts, **args):
        if opts.error: return func(body, opts, **args)

        opts.appid = body.get('appid', '')
        if len(opts.appid) != 40:
            opts.error = resp(opts.st, code=error.APPID_FORMAT,
                msg='Error AppId Format!'
            )
        return func(body, opts, **args)
    return check

def checkText(func):
    def check(body, opts, **args):
        if opts.error: return func(body, opts, **args)

        opts.text = body.get('text', opts.text).encode('utf8')
        if not opts.text or len(opts.text) > config.TEXT_LIMIT:
            opts.error = resp(opts.st, code=error.TEXT_LENGTH,
                msg= 'Title is less than 1 or '
                    'over than %d words' % config.TEXT_LIMIT
            )
        return func(body, opts, **args)
    return check

def checkTopic(func):
    def check(body, opts, **args):
        if opts.error: return func(body, opts, **args)

        opts.topic = body.get('topic', '')
        if not opts.topic or len(opts.topic) > config.TOPIC_LIMIT:
            opts.error = resp(opts.st, code=error.TOPIC_LENGTH,
                msg= 'Topic is less than 1 or '
                    'over than %d bytes'
            )
        elif noNumWords(opts.topic):
            opts.error = resp(opts.st, code=error.TOPIC_FORMAT,
                msg='Topic only is a combination of  numbers and words.'
            )
        return func(body, opts, **args)
    return check

def checkId(func):
    def check(body, opts, **args):
        if opts.error: return func(body, opts, **args)

        opts.Id = body.get('id')
        if not opts.Id:
            opts.error = resp(opts.st, code=error.ID_EMPTY,
                msg='ID is empty value!'
            )
        return func(body, opts, **args)
    return check

def checkKey(func):
    def check(body, opts, **args):
        if opts.error: return func(body, opts, **args)

        opts.key = body.get('key')
        if not opts.key:
            opts.error = resp(opts.st, code=error.KEY_EMPTY,
                msg='Search value is empty!'
            )
        return func(body, opts, **args)
    return check

def checkWeight(func):
    def check(body, opts, **args):
        if opts.error: return func(body, opts, **args)

        try:
            opts.w = float(body.get('w', opts.w))
        except Exception, e:
            opts.error = resp(opts.st, code=error.NUMBER_NEED,
                msg='Weight value must be number! (%s)' % body.get('w')
            )
        return func(body, opts, **args)
    return check

def getDBN(opts):
    _dbn = opts.db.searchMeta(opts.appid).get('DBN')
    if not _dbn:
        #寫入到search專用meta資料中
        return db.searchMeta(opts.appid, dbn=config.DEFAULT_DB)

    return _dbn

@checkAppid
@checkText
@checkTopic
@checkWeight
def post(body, opts):
    if opts.error: return opts.error

    _id = body.get('id', genId([opts.appid, opts.topic, opts.text]))

    _dbn = getDBN(opts)

    opts.db.set(_dbn)

    #如果opts.type不同需考慮不同的collection
    _col = opts.db.raw(opts.appid, opts.topic)
    _kw = opts.db.kw(opts.appid, opts.topic)
    try:
        _col.insert_one({
            'Id': _id,
            'text': opts.text,
            'w': opts.w,
            'UPT': opts.st,
        })

    except Exception, e:
        if 'duplicate key' in str(e):
            return resp(opts.st, code=error.DUPLICATE_KEY,
                msg= 'It already have the same topic, Id and Text!'
            )
        return resp(opts.st, code=error.CREATE_FAILED,
            msg=str(e)
        )

    _data = []
    try:
        for k in gram.get(f2j.get(opts.text)):
            _w = 1 if len(k) > 1 else 0.5
            _data.append({'Id':_id, 'key':k, 'w': _w * opts.w})

        _kw.insert_many(_data)

    except Exception, e:
        _col.delete_one({'Id': _id})

        return resp(opts.st, code=error.GRAM_PROCESS,
            msg=str(e)
        )

    return resp(opts.st, data=_id)

@checkAppid
@checkTopic
@checkId
def remove(body, opts, ctrl=False):
    if opts.error: return opts.error

    _dbn = getDBN(opts)

    opts.db.set(_dbn)

    #如果opts.type不同需考慮不同的collection
    _col = opts.db.raw(opts.appid, opts.topic)
    _kw = opts.db.kw(opts.appid, opts.topic, index=False)
    try:
        _col.delete_one({
            'Id': opts.Id,
        })
        _kw.delete_many({
            'Id': opts.Id,
        })

    except Exception, e:
        return resp(opts.st, code=error.DELETE_FAILED,
            msg=str(e)
        )

    if ctrl: return
    return resp(opts.st)

@checkAppid
@checkTopic
@checkId
def info(body, opts):
    if opts.error: return opts.error

    _dbn = getDBN(opts)

    opts.db.set(_dbn)

    #如果opts.type不同需考慮不同的collection
    _col = opts.db.raw(opts.appid, opts.topic)
    _kw = opts.db.kw(opts.appid, opts.topic)
    try:
        _data = _col.find_one({
            'Id': opts.Id,
            }, {'_id': 0})

        _data['key'] = _kw.count({'Id': opts.Id})

    except Exception, e:
        return resp(opts.st, code=error.QUERY_FAILED,
            msg=str(e)
        )

    return resp(opts.st, data=_data)

@checkAppid
@checkTopic
@checkKey
def search(body, opts):
    if opts.error: return opts.error

    _dbn = getDBN(opts)

    _or = []
    _data = []
    opts.db.set(_dbn)
    _kw = opts.db.kw(opts.appid, opts.topic)

    try:
        for k in gram.get(f2j.get(opts.key)):
            _or.append({'key': k})

    except Exception, e:
        return resp(opts.st, code=error.SEARCH_GRAM,
            msg=str(e)
        )

    try:
        for l in _kw.aggregate([
            {'$match': {'$or': _or}},
            {'$group' : {'_id': "$Id", 'rank': {'$sum': '$w'} } },
            {'$sort': {'rank': -1}},
            {'$skip': opts.skip},
            {'$limit': opts.limit}
        ]):
            _data.append(l)

    except Exception, e:
        return resp(opts.st, code=error.QUERY_FAILED,
            msg=str(e)
        )

    return resp(opts.st, data=_data)

def update(body, opts):
    _temp = remove(body, opts, ctrl=True)
    if _temp: return _temp
    return post(body, opts)

@checkAppid
@checkTopic
@checkId
@checkWeight
def realUpdate(body, opts):
    if opts.error: return opts.error

    try:
        _col = opts.db.raw(opts.appid, opts.topic)
        _col.update_one({
            'Id': opts.Id,
        }, {
            '$set': {'w': opts.w, 'UPT': opts.st}
        })
    except Exception, e:
        return resp(opts.st, code=error.UPDATE_FAILED,
            msg=str(e)
        )

    return resp(opts.st)

def command(body, opts):
    #if opts.error: return opts.error

    if body.get('method', '') == 'post':
        pass
    else: return resp(opts.st, msg='Method is Empty!')

    return resp(opts.st, msg='Command')
