# -*- encoding: utf8 -*-
import os, re
import sys
import json
import time

import data
import status
import make
import config

ROOT = os.path.dirname(__file__)

_HEADER_REQ_LIST = {
    'X-Droi-ReqID': 'ticket',
    'X-Droi-AppID': 'appID',
    'X-Droi-DeviceID': 'deviceID',
    'X-Droi-Remote-IP': 'remoteAddr',
    'X-Droi-Remote-Port': 'remotePort',
    'X-Droi-URI': 'uri',
    'X-Droi-Method': 'method',
    'action': 'action',
}

class Loader():

    def __init__(self, headers, result):
        self.header = headers
        self.method = headers.get('X-Droi-Method', 'main')
        self.appid = headers.get('X-Droi-Service-AppID')
        try:
            self.request = {
                'body': json.loads(headers.get('body', '')),
            }
        except ValueError:
            self.request = {
                'body': headers.get('body', ''),
            }

        self.result = result

        for k, kk in _HEADER_REQ_LIST.items():
            if k in headers:
                self.request[kk] = headers[k]

    def response(self):
        join = os.path.join
        exists = os.path.exists
        _path = self.header.get('path', '')

        _temp = join(ROOT, config.CODEBASE_TEMP)
        _target = join(join(_temp, self.appid), _path)

        if not exists(_target):
            _root = join(ROOT, config.CODEBASE_ROOT)
            _source = join(join(_root, self.appid), _path)
            if exists(_source):
                make.do(_source, _target)

            else:
                self.result.data = data.error(
                    status.MODULE_MISSING_FAILED,
                    msg='Source code is missing.',
                )

            return

        sys.path.append(os.path.dirname(_target))
        _m = os.path.basename(_target).strip('.py')

        try:
            exec('import %s as module' % _m)
            self.result.log = module.Droi._getLog
        except Exception, e:
            self.result.data = data.error(
                status.MODULE_IMPORT_FAILED,
                msg = str(e)
            )

            return

        try:
            exec('result=module.%s(self.request)' % self.method)
        except Exception, e:
            self.result.data = data.error(
                status.MODULE_RUNTIME_FAILED,
                msg = str(e)
            )
            return

        self.result.data = data.ok(result=result)
