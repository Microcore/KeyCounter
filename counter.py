#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyHook
import pythoncom
import win32api
import win32con
import win32event
import win32gui
import win32ui


class KeyCounter(object):

    def __init__(self):
        self.count = 0
        self.MESSAGE = win32gui.RegisterWindowMessage('KeyCounterValueUpdate')
        self.HWND = None
        self.hook = pyHook.HookManager()

    def hook_keyboard(self):
        def Key_handler(evt):
            self.count += 1
            window = getattr(self, 'HWND', None)
            if window is not None:
                win32gui.PostMessage(window, self.MESSAGE, self.count, 0)

        self.hook.KeyDown = Key_handler
        self.hook.HookKeyboard()

    def hook_mouse(self):
        pass

    def create_window(self):
        def wndProc(hWnd, message, wParam, lParam):
            if message == self.MESSAGE:
                win32gui.RedrawWindow(
                    hWnd, None, None, win32con.RDW_INVALIDATE
                )
                return 0
            if message == win32con.WM_PAINT:
                hdc, paintStruct = win32gui.BeginPaint(hWnd)

                dpiScale = win32ui.GetDeviceCaps(
                    hdc, win32con.LOGPIXELSX
                ) / 60.0
                fontSize = 36

                # http://msdn.microsoft.com/en-us/library/windows/desktop/dd145037(v=vs.85).aspx
                lf = win32gui.LOGFONT()
                lf.lfFaceName = "InputMono"
                lf.lfHeight = int(round(dpiScale * fontSize))
                # lf.lfWeight = 150
                # Use nonantialiased to remove the white edges around the text.
                lf.lfQuality = win32con.NONANTIALIASED_QUALITY
                hf = win32gui.CreateFontIndirect(lf)
                win32gui.SelectObject(hdc, hf)

                # rect = win32gui.GetClientRect(hWnd)
                rect = list(win32gui.GetClientRect(hWnd))
                # left, top, right, bottom
                rect[-1] = rect[-1] - 40
                rect = tuple(rect)
                # http://msdn.microsoft.com/en-us/library/windows/desktop/dd162498(v=vs.85).aspx
                win32gui.DrawText(
                    hdc,
                    str(self.count),
                    -1,
                    rect,
                    (win32con.DT_BOTTOM | win32con.DT_NOCLIP
                     | win32con.DT_SINGLELINE | win32con.DT_RIGHT)
                )
                win32gui.EndPaint(hWnd, paintStruct)
                return 0

            elif message == win32con.WM_DESTROY\
                    or message == win32con.WM_CLOSE\
                    or message == win32con.WM_DESTROY:
                print 'Closing the window.'
                win32gui.PostQuitMessage(0)
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
            | win32con.WS_EX_TRANSPARENT
        )

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms632600(v=vs.85).aspx
        # Consider using: WS_DISABLED, WS_POPUP, WS_VISIBLE
        style = win32con.WS_DISABLED | win32con.WS_POPUP | win32con.WS_VISIBLE

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms632680(v=vs.85).aspx
        hWindow = win32gui.CreateWindowEx(
            exStyle,
            wndClassAtom,
            None,  # WindowName
            style,
            0,  # x
            0,  # y
            win32api.GetSystemMetrics(win32con.SM_CXSCREEN),  # width
            win32api.GetSystemMetrics(win32con.SM_CYSCREEN),  # height
            None,  # hWndParent
            None,  # hMenu
            hInstance,
            None  # lpParam
        )

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633540(v=vs.85).aspx
        win32gui.SetLayeredWindowAttributes(
            hWindow, 0x00ffffff, 255,
            win32con.LWA_COLORKEY | win32con.LWA_ALPHA
        )

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

        self.HWND = hWindow

    def stop(self):
        win32gui.PostMessage(self.HWND, win32con.WM_CLOSE, 0, 0)
        win32gui.PostQuitMessage(0)

    def start(self):
        self.hook_keyboard()
        self.hook_mouse()
        self.create_window()

        while 1:
            try:
                win32event.MsgWaitForMultipleObjects(
                    [],
                    0,
                    16,
                    win32event.QS_ALLEVENTS
                )
                pythoncom.PumpWaitingMessages()
            except KeyboardInterrupt:
                print 'keyboard interrupt'
                self.stop()


if __name__ == '__main__':
    KeyCounter().start()
