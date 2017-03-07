# -*- encoding: utf8 -*-

_block = {'os', 'sys'}
"""
for l in _block:
    sys.modules[l] = None
"""

def _logStructure(lv, msg):
    import time
    return {'L': lv, 'M': msg, 'Ast': int(time.time())}

class DroiClass():

    def __init__(self):
        self._log = []

    def imports(self, module):
        if module in _block: return None
        elif type(module) is list:
            #實作dict回傳
            return {}

        exec('import %s as m' % module)
        return m

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

