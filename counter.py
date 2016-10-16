#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform


def start_counter():
    if platform.system() == 'Darwin':
        from keycounter.macos_counter import KeyCounter
    elif platform.system() == 'Windows':
        from keycounter.win32_counter import KeyCounter
    else:
        raise NotImplementedError(
            u'Un supported platform {}'.format(platform.system())
        )

    KeyCounter().start()


if __name__ == '__main__':
    start_counter()
