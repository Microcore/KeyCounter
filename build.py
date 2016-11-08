#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import platform
import subprocess
import sys

PYTHON_SCRIPTS_DIR = os.path.join(os.path.dirname(sys.executable), 'Scripts')
if platform.system() == 'Darwin':
    import dmgbuild


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
    dmgbuild.build_dmg(
        'dist/KeyCounter.dmg',
        'KeyCounter',
        'dmgbuild_conf.py',
        defines={}, lookForHiDPI=True
    )


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
