#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform


def patch_pyhook_64bit():
    # This patch comes from pyHook bug#1:
    # https://sourceforge.net/p/pyhook/bugs/1/
    import pyHook
    from PyHook import KeyboardEvent

    def KeyboardSwitch(
        self, msg, vk_code, scan_code, ascii, flags, time, hwnd, win_name
    ):
        event = KeyboardEvent(
            msg, vk_code, scan_code, ascii, flags, time, hwnd, win_name
        )
        # This seems to fix the annoying TypeError on 64bit Windows
        func = self.keyboard_funcs.get(int(str(msg)))
        if func:
            return func(event)
        else:
            return True
    pyHook.HookManager.KeyboardSwitch = KeyboardSwitch


def patch_all():
    if platform.system() == 'Windows'\
            and platform.architecture()[0].startswith('64'):
        patch_pyhook_64bit()
    if platform.system() == 'Darwin':
        pass
