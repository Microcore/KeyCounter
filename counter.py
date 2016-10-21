#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import platform
import sys

from keycounter.base_counter import __version__


def parse_options():
    '''Parse options and return result'''
    parser = argparse.ArgumentParser(version=__version__)
    parser.add_argument(
        '--port',
        metavar='N',
        type=int,
        default=-1,
        help='set the port for socket API server'
    )
    return parser.parse_args()


def start_counter():
    '''
    Start the counter, optionally start the API server.
    '''
    if platform.system() == 'Darwin':
        from keycounter.macos_counter import KeyCounter
    elif platform.system() == 'Windows':
        from keycounter.win32_counter import KeyCounter
    else:
        raise NotImplementedError(
            u'Un supported platform {}'.format(platform.system())
        )

    counter = KeyCounter()

    options = parse_options()
    if options.port != -1:
        # Warn about wrong port value and exit
        if options.port < 1024 or options.port > 65535:
            sys.stderr.write('Invalid port, must be in range of 1024 ~ 65536')
            sys.exit(1)
        else:
            # Start a thread for API server
            from keycounter.api import CountApiServer
            api_server = CountApiServer(options.port, counter)
            api_server.daemon = True
            api_server.start()

    counter.start()


if __name__ == '__main__':
    start_counter()
