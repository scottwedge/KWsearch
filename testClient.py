#!/usr/bin/env python
# -*- encoding: utf8 -*-
#Brief  Clinet testing for the mongodb backgroud service.
#Created 2017-05-25 @Evan

#import os
import time
import json
import argparse

import grpc
import miner_pb2
import miner_pb2_grpc

import config

__TIME_OUT = 5

CR = '\x1b[31m'
CW = '\x1b[37m'
CY = '\x1b[33m'
CG = '\x1b[32m'
CB = '\x1b[34m'

_appid = 'bf8umbzhigY-zYLSzOhEifAD91gTRXU2lQAAGsIK'
_topic = 'topic_test'

def main():
    """
    A description of this module and processing.
    """

    ch = grpc.insecure_channel('localhost:%d' % options.port)
    stub = miner_pb2_grpc.MinerStub(ch)

    print CB + '== POST ==' + CW
    resp = stub.post(
        miner_pb2.Request(
            body={
                'appid': _appid,
                'topic': _topic,
                'text': '測試內文',
            }),
        timeout=__TIME_OUT
    )

    _id = ''
    for k, v in resp.body.items():
        print k, ':', v
        if k == 'data': _id = v

    print CB + '== UPDATE ==' + CW
    resp = stub.update(
        miner_pb2.Request(
            body={
                'appid': _appid,
                'topic': _topic,
                'id': _id,
                'text': '測試天將降大任',
                'w': '5',
            }),
        timeout=__TIME_OUT
    )

    for k, v in resp.body.items():
        print k, ':', v

    print CB + '== INFO ==' + CW
    resp = stub.info(
        miner_pb2.Request(
            body={
                'appid': _appid,
                'topic': _topic,
                'id': _id,
            }),
        timeout=__TIME_OUT
    )

    for k, v in resp.body.items():
        print k, ':', v
    #"""

    print CB + '== SEARCH ==' + CW
    resp = stub.search(
        miner_pb2.Request(
            body={
                'appid': _appid,
                'topic': _topic,
                'key': '測試@',
            }),
        timeout=__TIME_OUT
    )

    for k, v in resp.body.items():
        print k, ':', v
    #"""

    print CB + '== REMOVE ==' + CW
    resp = stub.remove(
        miner_pb2.Request(
            body={
                'appid': _appid,
                'topic': _topic,
                'id': _id,
            }),
        timeout=__TIME_OUT
    )

    for k, v in resp.body.items():
        print k, ':', v
    #"""
    print
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=main.__doc__)

    parser.add_argument("-p", "--port", type=int,
        help="Port Number. (=%(default)s)",
        dest="port", default=7973) #required=False

    parser.add_argument("--host", type=str,
        help="Connection Host Address. (=%(default)s)",
        dest="host", default='localhost') #required=False


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


