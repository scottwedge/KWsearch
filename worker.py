#!/usr/bin/env python
# -*- encoding: utf8 -*-
#Brief  Miner broker
#Created 2013-07-09 @Evan
#LastUpdate 2017-02-10 @Evan :Change optparse to argparse

#import os
import argparse

#__name = os.path.basename(__file__)
#__path = os.path.dirname(__file__)
#if __path: os.chdir(__path)

def main():
    """
    A description of this module and processing.
    """
    print options.msg

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


