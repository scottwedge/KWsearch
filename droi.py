#!/usr/bin/env python
# -*- encoding: utf8 -*-
#Brief  Start the Droi.Py micro service.
#Created 2017-02-10 @Evan

#import os
import time
import argparse

from concurrent import futures

from threading import Thread

import grpc
import json
import droipy_pb2
import droipy_pb2_grpc

import config, status, data
import loader, hook, job, update

SECOND = 1000
_ONE_DAY_IN_SECONDS = 60 * 60 * 24
#__name = os.path.basename(__file__)
#__path = os.path.dirname(__file__)
#if __path: os.chdir(__path)

class Result():
    def __init__(self, data):
        self.data = data
        self.log = lambda : []

class Droi(droipy_pb2_grpc.DroiServicer):

    def loader(self, request, context):
        _st = time.time()

        _result = Result(data.error(
            status.MODULE_PROCESS_TIMEOUT,
            msg = 'Process Timeout: %ds' % config.CC_TIME_OUT
        ))

        _body = None

        try:
            module = loader.Loader(request.headers, _result)
            _td = Thread(target=module.response)
            _td.start()
            _td.join(int(config.CC_TIME_OUT))

            _body = _result.data
            json.dumps(_body) #for testing exception

        except TypeError, e:
            _body = data.ERROR(
                status.JSON_RETURN_FORMAT_ERROR,
                msg=str(e),
            )

        except Exception, e:
            _body = data.ERROR(
                status.UNKNOW_ERROR,
                msg=str(e),
            )
        finally:
            _temp = dict(request.headers)
            _body['pt'] = (time.time() - _st)*SECOND
            _body['log'] = _result.log()
            _temp['body'] = json.dumps(_body)
            return droipy_pb2.Response(
                headers=_temp
            )

    def hook(self, request, context):
        return droipy_pb2.Response(
            headers={'body': 'Hook isn\'t implement yet.'}
        )

    def job(self, request, context):
        return droipy_pb2.Response(
            headers={'body': 'Job isn\'t implement yet.'}
        )

    def update(self, request, context):
        _st = time.time()

        try:
            module = update.Update(request.headers)
            _body = module.response()
        except Exception, e:
            _body = data.ERROR(
                status.UNKNOW_ERROR,
                msg=str(e),
            )
        finally:
            _temp = dict(request.headers)
            _body['pt'] = (time.time() - _st)*SECOND
            _temp['body'] = json.dumps(_body)
            return droipy_pb2.Response(
                headers=_temp
            )


def main():
    """
    Start a GRPC micro service.
    """

    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=config.THREAD_POOL_NUM))
    droipy_pb2_grpc.add_DroiServicer_to_server(Droi(), server)
    for _pn in config.PORT_NUM:
        server.add_insecure_port('[::]:%d' % _pn)

    server.start()

    try:
        while True:
          time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=main.__doc__)

    parser.add_argument("-m", "--msg", type=str,
        help="Messages. (=%(default)s)",
        dest="msg", default="Hello World!") #required=False

    """
    parser.add_argument("-f", "--force", action="store_true",
        help="Force to do something right.",
        dest="force", default=False)

    parser.add_argument('numbers', type=int,
        help="Input Integer Array",
        nargs='*') #?,+,Num
    #"""
    options = parser.parse_args()

    parser.exit(main(), 'Done.')


