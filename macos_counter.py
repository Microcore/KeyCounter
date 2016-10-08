#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import signal
import sys

from AppKit import (
    NSApplication, NSApp, NSStatusBar, NSMenu, NSMenuItem,
)
from Cocoa import (
    NSKeyDownMask, NSKeyUpMask, NSFlagsChangedMask, NSEvent,
    NSKeyDown, NSKeyUp,
    NSApplicationActivationPolicyProhibited,
    NSImage,
)
from Foundation import NSObject
from PyObjCTools import AppHelper

from patch import patch_all
patch_all()

if getattr(sys, 'frozen', False):
    ROOT_PATH = os.path.dirname(sys.executable)
else:
    ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


class KeyCounter(object):

    def __init__(self):
        self.count = 0
        # 'KeyCounter',  # name
        # title=str(self.count),
        # icon=os.path.join(ROOT_PATH, 'resources', 'Keyboard-100.png')
        super(KeyCounter, self).__init__()
        self.key_count = 0
        self._title = str(self.key_count)
        self.icon = NSImage.alloc().initByReferencingFile_(
            os.path.join(ROOT_PATH, 'resources', 'Keyboard-100.png')
        )
        self.icon.setScalesWhenResized_(True)
        self.icon.setSize_((20, 20))
        self.icon.setTemplate_(True)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = '{}'.format(title)
        try:
            self.delegate.setStatusBarTitle()
        except AttributeError:
            pass

    def start(self):
        NSApplication.sharedApplication()
        self.delegate = self._create_app_delegate().alloc().init()
        NSApp().setDelegate_(self.delegate)
        NSApp().setActivationPolicy_(NSApplicationActivationPolicyProhibited)

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        self.delegate.initializeStatusBar()
        AppHelper.runEventLoop()

    def stop(self, *args):
        AppHelper.stopEventLoop()

    def reset_count(self):
        self.key_count = 0
        self.title = str(self.key_count)

    # Action alias for `quit:`
    def quit_(self, notification):
        self.stop()

    # Action alias for `reset:`
    def reset_(self, notification):
        self.reset_count()

    def _create_app_delegate(self):
        sc = self

        class AppDelegate(NSObject):

            def applicationDidFinishLaunching_(self, notification):
                mask = (NSKeyUpMask | NSFlagsChangedMask)
                NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, sc.handler)
                # rumps.rumps._log('Event handler set')

            def applicationWillResignActive(self, notification):
                self.applicationWillTerminate_(notification)
                return True

            def applicationShouldTerminate_(self, notification):
                print 'should terminate'
                self.applicationWillTerminate_(notification)
                return True

            def applicationWillTerminate_(self, notification):
                print 'will terminate'
                return None

            def initializeStatusBar(self):
                self.nsstatusitem = NSStatusBar.systemStatusBar().statusItemWithLength_(-1)  # variable dimensions
                self.nsstatusitem.setHighlightMode_(True)

                self.setStatusBarIcon()
                self.setStatusBarTitle()

                menu = NSMenu.alloc().init()
                # action `xxx:` will bind to `xxx_` method of delegate
                quit_menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    unicode('Quit'), 'quit:', ''
                )
                quit_menuitem.setTarget_(sc)

                reset_menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    unicode('Reset'), 'reset:', ''
                )
                reset_menuitem.setTarget_(sc)

                menu.addItem_(reset_menuitem)
                menu.addItem_(quit_menuitem)
                self.nsstatusitem.setMenu_(menu)  # mainmenu of our status bar spot (_menu attribute is NSMenu)

            def setStatusBarTitle(self):
                self.nsstatusitem.setTitle_(sc.title)

            def setStatusBarIcon(self):
                self.nsstatusitem.setImage_(sc.icon)

        return AppDelegate

    def handler(self, event):
        try:
            event_type = event.type()
            if event_type == NSKeyUp:
                print event.charactersIgnoringModifiers()
                self.key_count += 1
                self.title = str(self.key_count)
            else:
                pass
        except SystemExit:
            AppHelper.stopEventLoop()
        except:
            AppHelper.stopEventLoop()
            raise
