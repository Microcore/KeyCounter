#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import signal

from AppKit import (
    NSApplication, NSApp, NSStatusBar, NSMenu, NSMenuItem, NSWorkspace,
)
from Cocoa import (
    NSKeyUpMask, NSFlagsChangedMask, NSEvent,
    NSKeyUp, NSFlagsChanged, NSDeviceIndependentModifierFlagsMask,
    NSApplicationActivationPolicyProhibited,
)
from Foundation import NSObject, NSLog, NSURL
import objc
from PyObjCTools import AppHelper

from patch import patch_all
patch_all()

from .base_counter import BaseKeyCounter


class KeyCounter(BaseKeyCounter):

    # We'll be storing CSV data in Documents folder
    csv_file = os.path.expanduser('~/Documents/KeyCounter/data.csv')

    def __init__(self):
        super(KeyCounter, self).__init__()

    def update_ui(self):
        try:
            self.delegate.setStatusBarTitle()
        except AttributeError:
            pass

    def log(self, *args, **kwargs):
        if len(args) > 1:
            msg = args[0] % args[1:]
        elif len(args) == 1:
            msg = args[0]
        else:
            return
        NSLog(msg)

    def start(self):
        # Load today's count data back from data file
        super(KeyCounter, self).start()

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
        super(KeyCounter, self).stop()
        AppHelper.stopEventLoop()

    def _check_for_access(self):
        '''Check for accessibility permission'''
        # Because unsigned bundle will fail to call
        # AXIsProcessTrustedWithOptions with a segment falt, we're
        # not currently stepping into this function.
        return
        self.log('Begin checking for accessibility')
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
        self.log('Bundle com.apple.ApplicationServices loaded')
        try:
            if not AXIsProcessTrustedWithOptions(  # noqa
                {kAXTrustedCheckOptionPrompt: False}  # noqa
            ):
                self.log('Requesting access, Opening syspref window')
                NSWorkspace.sharedWorkspace().openURL_(
                    NSURL.alloc().initWithString_(
                        'x-apple.systempreferences:'
                        'com.apple.preference.security'
                        '?Privacy_Accessibility'
                    )
                )
        except:
            # Unsigned bundle will fail to call AXIsProcessTrustedWithOptions
            self.log((
                'Error detecting accessibility permission status, '
                'KeyCounter might not work'
            ))
        self.log('Access already granted')

    # Action alias for `quit:`
    def quit_(self, notification):
        self.stop()

    def _create_app_delegate(self):
        sc = self

        class AppDelegate(NSObject):

            def applicationDidFinishLaunching_(self, notification):
                mask = (NSKeyUpMask | NSFlagsChangedMask)
                NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
                    mask, sc.handle_keyevent
                )
                sc.log('Event match mask and hander set')

            def applicationWillResignActive(self, notification):
                self.applicationWillTerminate_(notification)
                return True

            def applicationShouldTerminate_(self, notification):
                sc.log('KeyCounter should terminate')
                self.applicationWillTerminate_(notification)
                return True

            def applicationWillTerminate_(self, notification):
                sc.log('KeyCounter will terminate')
                return None

            def _init_menu(self):
                menu = NSMenu.alloc().init()

                # App name menu
                appname_menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(  # noqa
                    u'{} {}'.format(unicode(sc.name), sc.version), None, ''
                )
                menu.addItem_(appname_menuitem)

                # Quit menu
                # action `xxx:` will bind to `xxx_` method of delegate
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

                self.setStatusBarTitle()
                self._init_menu()

            def setStatusBarTitle(self):
                self.nsstatusitem.setTitle_(str(sc.key_count))

        return AppDelegate

    def handle_keyevent(self, event):
        event_type = event.type()
        if event_type == NSKeyUp:
            super(KeyCounter, self).handle_keyevent(event)
        elif event_type == NSFlagsChanged:
            # Ref here: http://stackoverflow.com/a/6084359
            # TODO Fix Caps Lock key count, ref:
            # https://developer.apple.com/library/content/qa/qa1519/_index.html
            if event.modifierFlags() & NSDeviceIndependentModifierFlagsMask == 0:  # noqa
                super(KeyCounter, self).handle_keyevent(event)
