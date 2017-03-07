#!/usr/bin/env python
# -*- encoding: utf8 -*-
#Brief  Start the Droi.Py micro service.
#Created 2017-02-10 @Evan

#import os
import time
import json
import argparse

import grpc
import droipy_pb2
import droipy_pb2_grpc

import config
#__name = os.path.basename(__file__)
#__path = os.path.dirname(__file__)
#if __path: os.chdir(__path)

__TIME_OUT = 5#config.TIME_OUT

def main():
    """
    A description of this module and processing.
    """

    ch = grpc.insecure_channel('localhost:%d' % options.port)
    stub = droipy_pb2_grpc.DroiStub(ch)

    resp = stub.update(
        droipy_pb2.Request(
            headers={
                'X-Droi-Service-AppID': 'bf8umbzhigY-zYLSzOhEifAD91gTRXU2lQAAGsIK',
                'X-Droi-Method': 'update',
                'path': 'py/testm.py'
            }),
        timeout=__TIME_OUT
    )

    for k, v in resp.headers.items():
        print k, ':', v

    print
    for i in xrange(options.times):
        try:
            resp = stub.loader(
                droipy_pb2.Request(
                    headers={
                        'X-Droi-Service-AppID': 'bf8umbzhigY-zYLSzOhEifAD91gTRXU2lQAAGsIK',
                        'X-Droi-Method': 'test',
                        'X-Droi-Remote-IP': 'localhost',
                        'path': 'py/testm.py',
                        'body': json.dumps({
                            'tag': 'loader', 'num': i
                        })
                    }),
                timeout=__TIME_OUT
            )

            for k, v in resp.headers.items():
                print k, ':', v

        except Exception, e:
            print e
            break
        time.sleep(1)

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=main.__doc__)

    parser.add_argument("-p", "--port", type=int,
        help="Port Number. (=%(default)s)",
        dest="port", default=50051) #required=False

    parser.add_argument("-t", "--times", type=int,
        help="Execute Times. (=%(default)s)",
        dest="times", default=10) #required=False

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


