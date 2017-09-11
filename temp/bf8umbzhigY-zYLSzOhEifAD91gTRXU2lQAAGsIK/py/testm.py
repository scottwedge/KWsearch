# -*- encoding: utf8 -*-
import grpc
import mongo_pb2
import mongo_pb2_grpc

import dbsdk as _dbsdk
import config as _config

_block = {'os', 'sys'}

def _logStructure(lv, msg):
    import time as __t
    return {'L': lv, 'M': msg, 'Ast': int(__t.time())}

class Modules():
    def __init__(self, module=[]):
        for _m in module:
            exec('import %s as m;self.%s = m' % (
                _m, _m
            ))

    def getNames(self):
        return self.__dict__.keys()

    def remove(self, name):
        del self.__dict__[name]

    def _merge(self, Ms):
        self.__dict__.update(Ms.__dict__)

class DroiClass():

    def __init__(self):
        self._log = []
        self.modules = Modules()

        _ch = grpc.insecure_channel(
            '%s:%d' % (
                _config.DB_API_HOST,
                int(_config.DB_API_PORT)
            ))

        self._grpc = mongo_pb2_grpc.MongoStub(_ch)

    def Object(self, *args, **options):
        return _dbsdk.Object(
            self._grpc, self.__header, _config.TIME_OUT, args, options)

    def _setHeader(self, header):
        self.__header = header

    def imports(self, module):
        if type(module) is list:
            #實作dict回傳
            _module = []
            for _m in module:
                if _m in _block: continue
                _module.append(_m)

            __M = Modules(_module)
            self.modules._merge(__M)
            return __M

        elif module in _block: return None
        elif type(module) is str:
            exec('import %s as _m' % module)
            self.modules.__dict__[module] = _m
            return _m

        raise Exception('[Droi.imports] Import Error Type %s (%s)' % (
                    type(module), module))

    def _getLog(self):
        _temp = self._log
        self._log = []
        return _temp

    def log(self, text):
        self._log.append(_logStructure("INFO", text))

    def debug(self, text):
        self._log.append(_logStructure("DEBUG", text))

    def warning(self, text):
        self._log.append(_logStructure("WARN", text))

    def error(self, text):
        self._log.append(_logStructure("ERR", text))


Droi = DroiClass()


def unitest(req):

    _resp = Droi.Object('DroiObjectApi', '56cea1d8c9922205b5bdfab7', oid='63db9883274df63927c1e474').fetch()
    return _resp.getResult()


def test(req):
    Droi.imports(['time'])
    Droi.imports(['os', 'md5'])
    Droi.modules.remove('md5')
    Droi.imports('md5')
    obj = Droi.modules
    md5 = obj.md5.md5
    Droi.error(md5('test').hexdigest())

    return Droi.Object('test', 'user').echo('test')
    return '%s/%s/%s' % obj.time.localtime()[:3]
    Droi.log('香雞堡')
    return req['body']['num']

