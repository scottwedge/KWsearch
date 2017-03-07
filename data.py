import json

def ERROR(*args, **options):
    return json.dumps(error(*args, **options))

def OK(*args, **options):
    return json.dumps(ok(*args, **options))


def error(code, msg="", pt=None, **others):
    _temp = {
        'code': code,
        'msg': msg,
    }

    if pt: _temp['pt'] = pt
    for k, v in others.items():
        _temp[k] = v

    return _temp

def ok(pt=None, **others):
    _temp = {
        'code': 0,
        'pt': pt,
    }

    if pt: _temp['pt'] = pt
    for k, v in others.items():
        _temp[k] = v

    return _temp
