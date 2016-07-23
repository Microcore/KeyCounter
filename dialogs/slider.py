#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pywin.mfc import dialog
import win32con
import win32ui


class TransparencySliderDialog(dialog.Dialog):
    '''Simple dialog with a single trackbar control inside'''
    _dialogstyle = (
        win32con.WS_DLGFRAME |
        win32con.DS_MODALFRAME | win32con.WS_POPUP | win32con.WS_VISIBLE |
        win32con.WS_CAPTION | win32con.WS_SYSMENU | win32con.DS_SETFONT
    )
    _buttonstyle = (
        win32con.BS_PUSHBUTTON | win32con.WS_TABSTOP |
        win32con.WS_CHILD | win32con.WS_VISIBLE
    )
    _labelStyle = win32con.WS_CHILD | win32con.WS_VISIBLE
    DIALOGTEMPLATE = [
        [
            'Transparency',
            (0, 0, 155, 40),  # x, y, w, h
            _dialogstyle, None,
            (11, 'Microsoft YaHei')
        ],
        [
            130, 'Transparent', -1, (5, 0, 60, 10),
            _labelStyle | win32con.SS_LEFT
        ],
        [
            130, 'Opaque', -1, (125, 0, 60, 10),
            _labelStyle | win32con.SS_LEFT
        ],
        [
            128, 'Ok', win32con.IDOK, (55, 20, 45, 14),
            _buttonstyle
        ],
    ]
    IDC_SLIDER = 9500

    def __init__(self, init_value=0, on_value=None):
        dialog.Dialog.__init__(self, self.DIALOGTEMPLATE)
        self.init_value = init_value
        self.on_value = on_value

    def OnInitDialog(self):
        rc = dialog.Dialog.OnInitDialog(self)
        win32ui.EnableControlContainer()
        self.slider = win32ui.CreateSliderCtrl()
        self.slider.CreateWindow(
            win32con.WS_TABSTOP | win32con.WS_VISIBLE,
            (105, 0, 280, 30),
            self._obj_,
            self.IDC_SLIDER
        )
        self.slider.SetRange(0, 255)
        self.slider.SetPos(self.init_value)
        self.slider.SetTic(self.init_value)
        self.HookMessage(self.OnSliderMove, win32con.WM_HSCROLL)
        return rc

    def OnSliderMove(self, params):
        if callable(self.on_value):
            self.on_value(self.slider.GetPos())

    def OnOK(self):
        if callable(self.on_value):
            self.on_value(self.slider.GetPos())
        self._obj_.OnOK()

    def OnClose(self):
        if callable(self.on_value):
            self.on_value(self.slider.GetPos())
        self._obj_.OnClose()


if __name__ == '__main__':
    tDialog = TransparencySliderDialog(128)
    tDialog.DoModal()
