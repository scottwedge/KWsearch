#!/usr/bin/env python
# -*- encoding: utf8 -*-
#Brief  Start the Miner GRPC Service.
#Created 2017-08-09 @Evan

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

from pymongo import MongoClient

import config
import error
import broker

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
#__name = os.path.basename(__file__)
#__path = os.path.dirname(__file__)
#if __path: os.chdir(__path)

def package(action, body):
    _st = time.time()
    return action(body, Options(_st))
    try:
        return action(body, Options(_st))
    except Exception, e:
        if 'not authorized' in str(e):
            return broker.resp(_st, code=error.AUTHORIZED_PERMISSION,
                msg='SE No Permission, Please feadback to Droi Co.'
            )

        return broker.resp(_st, code=error.UNKNOW,
            msg=str(e)
        )

class Options():
    def __init__(self, timestamp):
        self.st = timestamp
        self.error = None
        self.db = _mongo
        self.type = 'title'
        self.w = 1
        self.text = ''
        self.limit = 10
        self.skip = 0

class Mongo():
    def __init__(self, mode):
        self.conn = MongoClient(config.DB_HOST[mode],
            #serverSelectionTimeoutMS=1000,
            connectTimeoutMS=500,
            #socketTimeoutMS=500,
            #maxIdleTimeMS=1000,
            minPoolSize=10,
        )

        self.conn.get_database('admin').authenticate(
            config.DB_USER, config.DB_PSWD)
        self.dbops = self.conn.get_database(config.DB_NAME)

    def set(self, name):
        self.db = self.conn.get_database(name)

    def col(self, name):
        return self.db.get_collection(name)

    def raw(self, appid, topic, index=True):
        _raw = '%s.%s.raw' % (appid, topic)
        _col = self.col(_raw)
        if not index: return _col

        _indexes = []
        for l in _col.list_indexes():
            _idx = dict(l)
            _indexes += _idx.get('key', {}).to_dict().keys()

        if 'Id' not in _indexes:
            _col.create_index([('Id', 1)], background=True, unique=True)
            _col.create_index([('UPT', 1)], background=True)

        return _col

    def kw(self, appid, topic, index=True):
        _raw = '%s.%s.kw' % (appid, topic)
        _col = self.col(_raw)
        if not index: return _col

        _indexes = []
        for l in _col.list_indexes():
            _idx = dict(l)
            _indexes += _idx.get('key', {}).to_dict().keys()

        if 'Id' not in _indexes:
            _col.create_index([('Id', 1)], background=True)
            _col.create_index([('key', 1)], background=True)

        return _col

    def searchMeta(self, appid, dbn=None):
        if dbn:
            self.dbops.get_collection('searchMeta').insert_one(
                {'AppId': appid, 'DBN': dbn}
            )

        _data = self.dbops.get_collection('searchMeta').find_one(
            {'AppId': appid}, {'DBN': 1, '_id': 0}
        )
        if _data: return _data
        return {}

    def appMeta(self, appid=None):
        if appid:
            _data = self.dbops.get_collection('_AppMeta').find_one(
                {'AppId': appid}, {'DBN': 1, '_id': 0}
            )
            if _data: return _data
            return {}

        for l in self.dbops.get_collection('_AppMeta').find(
            {}, {'DBN': 1, '_id': 0, 'AppId': 1}
        ):
            return l

        return {}


class Miner(miner_pb2_grpc.MinerServicer):

    def post(self, request, context):
        return package(broker.post, request.body)

    def remove(self, request, context):
        return package(broker.remove, request.body)

    def info(self, request, context):
        return package(broker.info, request.body)

    def search(self, request, context):
        return package(broker.search, request.body)

    def update(self, request, context):
        return package(broker.update, request.body)

    def command(self, request, context):
        return package(broker.command, request.body)

def main():
    """
    Start a GRPC micro service.
    """
    _port = options.port if options.port else config.PORT_NUM

    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=config.THREAD_POOL_NUM))
    miner_pb2_grpc.add_MinerServicer_to_server(Miner(), server)
    server.add_insecure_port('[::]:%d' % _port)

    server.start()

    try:
        while True:
          time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=main.__doc__)

    parser.add_argument("-p", "--port", type=int,
        help="Port Number. (=%(default)s)",
        dest="port") #required=False

    parser.add_argument("-m", "--mode", type=str,
        help="Execution Mode. (=%(default)s)",
        dest="mode", default='alpha') #required=False

    """
    parser.add_argument("-f", "--force", action="store_true",
        help="Force to do something right.",
        dest="force", default=False)

    parser.add_argument('numbers', type=int,
        help="Input Integer Array",
        nargs='*') #?,+,Num
    #"""
    options = parser.parse_args()

    _mongo = Mongo(options.mode)

    parser.exit(main(), 'Done.')


