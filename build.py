#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform
import subprocess
import sys


def execute(cmd):
    '''Excute a command'''
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    sys.stdout.write(out)
    sys.stderr.write(err)


def build_macos():
    '''
    Build DMG for macOS platform
    '''
    execute([
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'counter.spec',
    ])
    execute([
        'dmgbuild', '-s', 'dmgbuild_conf.py',
        'KeyCounter',
        'dist/KeyCounter.dmg',
    ])


def build_win32():
    '''
    Build EXE for win32 platform
    '''
    execute([
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'counter.spec',
    ])


def main():
    if platform.system() == 'Windows':
        build_win32()
    elif platform.system() == 'Darwin':
        build_macos()
    else:
        sys.stderr.write('Unsupported platform')
        sys.exit(1)


if __name__ == '__main__':
    main()