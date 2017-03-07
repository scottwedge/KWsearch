import os
import re
import codecs

import config

def do(source, target):
    _path = os.path.dirname(target)
    if not os.path.exists(_path):
        os.makedirs(_path)
        os.popen('touch ' + os.path.join(_path, '__init__.py'))

    bf = codecs.open(config.BLOCK, 'r', 'utf8')
    sf = codecs.open(source, 'r', 'utf8')
    with codecs.open(target, 'w', 'utf8') as tf:
        tf.write(bf.read())
        _line = 1
        for l in sf:
            if re.match('[ \t]*#', l): continue
            if re.search('([^a-zA-Z\d]*import |[ ]*exec\()', l):
                raise Exception(
                    '[LINE: %d] "import" and "exec" '
                    'are both forbidden. ' % (_line, )
                )
            tf.write(l)

    bf.close()
    sf.close()

