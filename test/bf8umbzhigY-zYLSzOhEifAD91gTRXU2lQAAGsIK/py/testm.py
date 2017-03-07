
def test(req):
    time = Droi.imports('time')
    md5 = Droi.imports('md5')
    Droi.error(md5.md5('test').hexdigest())

    #time.sleep(2)

    Droi.log('香雞堡')
    return req['body']['num']
