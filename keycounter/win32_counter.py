#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

import patch
patch.patch_all()

import pyHook
import win32api
import win32con
import win32event
import win32gui
import win32gui_struct
import win32ui
import winerror

from .base_counter import BaseKeyCounter


class KeyCounter(BaseKeyCounter):

    def __init__(self):
        super(KeyCounter, self).__init__()

        self.HWND = None
        self.hook = pyHook.HookManager()
        self.FPS = 60
        self.MSPF = int(round(1000.0 / self.FPS))
        self.font = None
        self.tooltip = 'Key Counter'
        # Private message to be used in THIS program ONLY
        self.MESSAGE = random.randint(win32con.WM_USER, 0x7FFF)
        self.__MESSAGE_TC = win32gui.RegisterWindowMessage('TaskbarCreated')
        self.__NOTIFY_ID = None
        self.MENU = None
        self.APP_NAME = u'{} {}'.format(self.name, self.version)
        self.MENU_FUNCS = {
            'Quit': self.stop,
        }
        self.MENU_TEXTS = [self.APP_NAME, 'Quit', ][::-1]
        self.__last_text_extent = (0, 0)
        self.SICHECK_EVENT = None
        self.GUID = '76B80C3C-11AB-47CD-A124-BADB07F41DB8'

    def update_ui(self):
        win32gui.RedrawWindow(self.HWND, None, None, win32con.RDW_INVALIDATE)

    def hook_keyboard(self):
        self.hook.KeyUp = self.handle_keyevent
        self.hook.HookKeyboard()

    def init_font(self, hdc, paintStruct):
        # http://msdn.microsoft.com/en-us/library/windows/desktop/dd145037(v=vs.85).aspx
        lf = win32gui.LOGFONT()
        lf.lfFaceName = "InputMono"
        fontSize = 36
        dpiScale = win32ui.GetDeviceCaps(
            hdc, win32con.LOGPIXELSX
        ) / 60.0
        lf.lfHeight = int(round(dpiScale * fontSize))
        # lf.lfWeight = 150
        # Use nonantialiased to remove the white edges around the text.
        # lf.lfQuality = win32con.NONANTIALIASED_QUALITY
        lf.lfQuality = win32con.NONANTIALIASED_QUALITY
        self.font = win32gui.CreateFontIndirect(lf)

    def create_menu(self):
        '''Create context menu'''
        if self.MENU is not None:
            return
        self.MENU = win32gui.CreatePopupMenu()
        # Add menu items
        # Insert backwards
        # https://msdn.microsoft.com/en-us/library/windows/desktop/ms647988(v=vs.85).aspx

        # Quit
        win32gui.InsertMenuItem(
            self.MENU,
            0,
            1,
            win32gui_struct.PackMENUITEMINFO(text='Quit', wID=0)[0]
        )
        # App name
        win32gui.InsertMenuItem(
            self.MENU,
            0,
            1,
            win32gui_struct.PackMENUITEMINFO(
                text='KeyCounter', wID=0, fState=win32con.MFS_DISABLED
            )[0]
        )

    def show_menu(self):
        if self.MENU is None:
            self.create_menu()
        position = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.HWND)
        win32gui.TrackPopupMenu(
            self.MENU,
            win32con.TPM_LEFTALIGN,
            position[0],
            position[1],
            0,
            self.HWND,
            None
        )
        win32gui.PostMessage(self.HWND, win32con.WM_NULL, None, None)

    def execute_menu_item(self, index):
        '''Execute menu item function'''
        func = self.MENU_FUNCS.get(self.MENU_TEXTS[index], None)
        if callable(func):
            func()

    def create_window(self):
        def wndProc(hWnd, message, wParam, lParam):
            if message == self.MESSAGE:
                if lParam == win32con.WM_RBUTTONUP:
                    self.show_menu()
                return 0
            elif message == win32con.WM_COMMAND:
                self.execute_menu_item(win32gui.LOWORD(wParam))
                return 0
            elif message == self.__MESSAGE_TC:
                self.update_tray_icon()
                return 0
            elif message == win32con.WM_PAINT:
                hdc, paintStruct = win32gui.BeginPaint(hWnd)
                if self.font is None:
                    self.init_font(hdc, paintStruct)
                # Set the font
                win32gui.SelectObject(hdc, self.font)

                text = str(self.key_count)
                # Clear window content
                win32gui.DefWindowProc(hWnd, message, wParam, lParam)

                # Dynamically change window size & position if necessary
                text_extent = win32gui.GetTextExtentPoint32(hdc, text)
                window_rect = win32gui.GetClientRect(hWnd)
                window_width = window_rect[2] - window_rect[0]
                window_height = window_rect[3] - window_rect[1]

                if window_width != text_extent[0]\
                        or window_height != text_extent[1]:
                    screen_width = win32api.GetSystemMetrics(
                        win32con.SM_CXSCREEN
                    )
                    screen_height = win32api.GetSystemMetrics(
                        win32con.SM_CYSCREEN
                    )
                    win32gui.SetWindowPos(
                        self.HWND,
                        None,
                        screen_width - text_extent[0],  # x
                        screen_height - text_extent[1] - 40,  # y, height of taskbar  # noqa
                        text_extent[0],  # width
                        text_extent[1],  # height
                        0
                    )
                # http://msdn.microsoft.com/en-us/library/windows/desktop/dd162498(v=vs.85).aspx
                win32gui.DrawText(
                    hdc,
                    text,
                    len(text),  # somehow -1 does not work
                    tuple(win32gui.GetClientRect(hWnd)),
                    (win32con.DT_BOTTOM | win32con.DT_NOCLIP
                     | win32con.DT_SINGLELINE | win32con.DT_RIGHT)
                )
                self.__last_text_extent = text_extent
                win32gui.EndPaint(hWnd, paintStruct)
                return 0

            elif message == win32con.WM_DESTROY:
                self.log('Window destroyed')
                return 0
            elif message == win32con.WM_CLOSE:
                self.log('Closing the window')
                return 0

            else:
                return win32gui.DefWindowProc(hWnd, message, wParam, lParam)

        hInstance = win32api.GetModuleHandle()
        className = 'TransparentWindow'

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633576(v=vs.85).aspx
        # win32gui does not support WNDCLASSEX.
        wndClass = win32gui.WNDCLASS()
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ff729176(v=vs.85).aspx
        wndClass.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wndClass.lpfnWndProc = wndProc
        wndClass.hInstance = hInstance
        wndClass.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
        wndClass.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        wndClass.lpszClassName = className
        # win32gui does not support RegisterClassEx
        wndClassAtom = win32gui.RegisterClass(wndClass)

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ff700543(v=vs.85).aspx
        # Consider using:
        #     WS_EX_COMPOSITED, WS_EX_LAYERED, WS_EX_NOACTIVATE,
        #     WS_EX_TOOLWINDOW, WS_EX_TOPMOST, WS_EX_TRANSPARENT
        # The WS_EX_TRANSPARENT flag makes events (like mouse clicks)
        # fall through the window.
        exStyle = (
            win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED
            | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST
            | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOOLWINDOW
        )

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms632600(v=vs.85).aspx
        # Consider using: WS_DISABLED, WS_POPUP, WS_VISIBLE
        style = win32con.WS_DISABLED | win32con.WS_POPUP | win32con.WS_VISIBLE

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms632680(v=vs.85).aspx
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        # We'll update window size if we need more space
        init_width = 1
        init_height = 1
        hWindow = win32gui.CreateWindowEx(
            exStyle,
            wndClassAtom,
            None,  # WindowName
            style,
            screen_width - init_width,  # x
            screen_height - init_height,  # y
            init_width,  # width
            init_height,  # height
            None,  # hWndParent
            None,  # hMenu
            hInstance,
            None  # lpParam
        )
        self.HWND = hWindow

        # Foreground transparency of 208 looks good
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633540(v=vs.85).aspx
        win32gui.SetLayeredWindowAttributes(
            self.HWND,
            0x00ffffff,
            208,  # foreground transparency, 255 means opaque
            win32con.LWA_COLORKEY | win32con.LWA_ALPHA
        )

        # Transparent background
        win32gui.SetBkMode(hWindow, win32con.TRANSPARENT)

        # http://msdn.microsoft.com/en-us/library/windows/desktop/dd145167(v=vs.85).aspx
        # win32gui.UpdateWindow(hWindow)

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633545(v=vs.85).aspx
        win32gui.SetWindowPos(
            hWindow, win32con.HWND_TOPMOST, 0, 0, 0, 0,
            (win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE
             | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
        )

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633548(v=vs.85).aspx
        # win32gui.ShowWindow(hWindow, win32con.SW_SHOW)

    def update_tray_icon(self):
        try:
            hIcon = win32gui.LoadIcon(
                win32gui.GetModuleHandle(None), win32con.IDI_APPLICATION
            )
        except:
            hIcon = win32gui.LoadIcon(None, win32con.IDI_APPLICATION)
        if self.__NOTIFY_ID is None:
            message = win32gui.NIM_ADD
        else:
            message = win32gui.NIM_MODIFY
        self.__NOTIFY_ID = (
            self.HWND,
            0,
            win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
            self.MESSAGE,
            hIcon,
            self.tooltip
        )
        win32gui.Shell_NotifyIcon(message, self.__NOTIFY_ID)

    def instance_running(self):
        '''
        Use CreateEvent to make sure there is only one instance running
        '''
        if self.SICHECK_EVENT is None:
            self.SICHECK_EVENT = win32event.CreateEvent(
                None, 1, 0, self.GUID
            )
            # An instance is already running, quit
            if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
                win32gui.MessageBox(
                    self.HWND,
                    'You can only run one instance at a time',
                    'Seems like KeyCounter is already running',
                    win32con.MB_OK
                )
                return self.stop()

    def clear_instance_check_event(self):
        '''Close handle created by CreateEvent'''
        if self.SICHECK_EVENT is not None:
            win32api.CloseHandle(self.SICHECK_EVENT)

    def stop(self):
        if getattr(self, 'hook', None) is not None:
            del self.hook
        if self.HWND is not None:
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self.HWND, 0))
            # win32gui.PostMessage(self.HWND, win32con.WM_CLOSE, 0, 0)
            win32gui.DestroyWindow(self.HWND)
            self.HWND = None
        self.clear_instance_check_event()

        super(KeyCounter, self).stop()
        raise SystemExit(0)

    def start(self):
        if self.instance_running():
            try:
                self.stop()
            except SystemExit:
                return win32gui.PostQuitMessage(0)

        # Load today's count data back from data file
        super(KeyCounter, self).start()

        self.hook_keyboard()
        self.create_window()
        self.update_tray_icon()

        while 1:
            try:
                win32event.MsgWaitForMultipleObjects(
                    [],
                    0,
                    self.MSPF,
                    win32event.QS_ALLEVENTS
                )
                win32gui.PumpWaitingMessages()
            except SystemExit:
                win32gui.PostQuitMessage(0)


if __name__ == '__main__':
    KeyCounter().start()
