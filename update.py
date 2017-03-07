import os
import sys
import json

import data
import status
import make
import config

#__name = os.path.basename(__file__)
ROOT = os.path.dirname(__file__)

class Update():

    def __init__(self, headers):
        self.header = headers
        self.method = headers.get('X-Droi-Method', 'main')
        self.appid = headers.get('X-Droi-Service-AppID')
        self.body = json.loads(headers.get('body', '{}'))

    def response(self):
        join = os.path.join
        exists = os.path.exists
        _path = self.header.get('path', '')

        _temp = join(ROOT, config.CODEBASE_TEMP)
        _target = join(join(_temp, self.appid), _path)

        try:
            os.remove(_target)
        except: pass

        if not exists(_target):
            _root = join(ROOT, config.CODEBASE_ROOT)
            _source = join(join(_root, self.appid), _path)
            if exists(_source):
                try:
                    make.do(_source, _target)
                except Exception, e:
                    return data.error(
                        status.MODULE_PACKFILE_FAILED,
                        msg = str(e)
                    )

            else: return data.error(
                    status.MODULE_MISSING_FAILED,
                    msg='Source code is missing.'
                )

        sys.path.append(os.path.dirname(_target))
        _m = os.path.basename(_target).strip('.py')

        try:
            exec('import %s as module' % _m)
            reload(module) #v3.x imp.reload
        except Exception, e:
            return data.error(
                status.MODULE_UPDATE_FAILED,
                msg = str(e)
            )

        return data.ok(tag='update')
