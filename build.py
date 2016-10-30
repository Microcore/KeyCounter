#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import platform
import subprocess
import sys

import dmgbuild

PYTHON_SCRIPTS_DIR = os.path.join(os.path.dirname(sys.executable), 'Scripts')
DMGBUILD_SCRIPT = os.path.join(
    os.path.dirname(dmgbuild.__file__), 'scripts', 'dmgbuild'
)


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
        sys.executable,
        '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'counter.spec',
    ])
    execute([
        sys.executable,
        '-m', DMGBUILD_SCRIPT,
        '-s', 'dmgbuild_conf.py',
        'KeyCounter',
        'dist/KeyCounter.dmg',
    ])


def build_win32():
    '''
    Build EXE for win32 platform
    '''
    execute([
        os.path.join(PYTHON_SCRIPTS_DIR, 'pyinstaller'),
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
