#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import signal
import sys
import webbrowser

from AppKit import (
    NSApplication, NSApp, NSStatusBar, NSMenu, NSMenuItem, NSWorkspace,
)
from Cocoa import (
    NSKeyUpMask, NSFlagsChangedMask, NSEvent,
    NSKeyUp,
    NSApplicationActivationPolicyProhibited,
    NSImage,
)
from Foundation import NSObject, NSLog, NSURL
import objc
from PyObjCTools import AppHelper

from patch import patch_all
patch_all()


def log(*args):
    NSLog(' '.join(map(str, args)))


class KeyCounter(object):

    def __init__(self):
        super(KeyCounter, self).__init__()
        self.name = 'KeyCounter'
        self.key_count = 0
        self.icon = None

        self.title = str(self.key_count)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title
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

        self._check_for_access()

        self.delegate.initializeStatusBar()
        AppHelper.runEventLoop()

    def stop(self, *args):
        AppHelper.stopEventLoop()

    def reset_count(self):
        self.key_count = 0
        self.title = str(self.key_count)

    def _check_for_access(self):
        '''Check for accessibility permission'''
        # Because unsigned bundle will fail to call
        # AXIsProcessTrustedWithOptions with a segment falt, we're
        # not currently stepping into this function.
        return
        log('Begin checking for accessibility')
        core_services = objc.loadBundle(
            'CoreServices',
            globals(),
            bundle_identifier='com.apple.ApplicationServices'
        )
        objc.loadBundleFunctions(
            core_services,
            globals(),
            [('AXIsProcessTrustedWithOptions', b'Z@')]
        )
        objc.loadBundleFunctions(
            core_services,
            globals(),
            [('kAXTrustedCheckOptionPrompt', b'@')]
        )
        log('Bundle com.apple.ApplicationServices loaded')
        try:
            if not AXIsProcessTrustedWithOptions({kAXTrustedCheckOptionPrompt: False}):
                log('Requesting access, Opening syspref window')
                NSWorkspace.sharedWorkspace().openURL_(
                    NSURL.alloc().initWithString_(
                        'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
                    )
                )
        except:
            # Unsigned bundle will fail to call AXIsProcessTrustedWithOptions
            log('Error detecting accessibility permission status, KeyCounter might not work')
        log('Access already granted')

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
                NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
                    mask, sc.handler
                )
                log('Event match mask and hander set')

            def applicationWillResignActive(self, notification):
                self.applicationWillTerminate_(notification)
                return True

            def applicationShouldTerminate_(self, notification):
                log('KeyCounter should terminate')
                self.applicationWillTerminate_(notification)
                return True

            def applicationWillTerminate_(self, notification):
                log('KeyCounter will terminate')
                return None

            def _init_menu(self):
                menu = NSMenu.alloc().init()

                # App name menu
                appname_menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(  # noqa
                    unicode(sc.name), None, ''
                )
                menu.addItem_(appname_menuitem)

                # Reset menu
                # action `xxx:` will bind to `xxx_` method of delegate
                reset_menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(  # noqa
                    unicode('Reset'), 'reset:', 'n'
                )
                # Tell objc to look for action method in this specific object
                reset_menuitem.setTarget_(sc)
                menu.addItem_(reset_menuitem)

                # Separator
                menu.addItem_(NSMenuItem.separatorItem())

                # Quit menu
                quit_menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(  # noqa
                    unicode('Quit'), 'quit:', 'q'
                )
                quit_menuitem.setTarget_(sc)
                menu.addItem_(quit_menuitem)

                self.nsstatusitem.setMenu_(menu)

            def initializeStatusBar(self):
                self.nsstatusitem = NSStatusBar.systemStatusBar().statusItemWithLength_(-1)  # noqa
                self.nsstatusitem.setHighlightMode_(True)
                # This does not seem to work, we'll display a menu item instead
                # self.nsstatusitem.setToolTip_('KeyCounter')

                self.setStatusBarIcon()
                self.setStatusBarTitle()
                self._init_menu()

            def setStatusBarTitle(self):
                self.nsstatusitem.setTitle_(sc.title)

            def setStatusBarIcon(self):
                if sc.icon is not None:
                    self.nsstatusitem.setImage_(sc.icon)

        return AppDelegate

    def handler(self, event):
        try:
            event_type = event.type()
            if event_type == NSKeyUp:
                self.key_count += 1
                self.title = str(self.key_count)
            else:
                pass
        except SystemExit:
            AppHelper.stopEventLoop()
        except:
            AppHelper.stopEventLoop()
            raise
