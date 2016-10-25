#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from keycounter.base_counter import BaseKeyCounter


class BaseKeyCounterTest(unittest.TestCase):
    '''Unit test for BaseKeyCounter class'''

    def setUp(self):
        self.counter = BaseKeyCounter()
        self.counter.update_ui = lambda: None
        self.counter.start()
        # We'll reset the count to init value so we don't mess up real data
        self.init_count = self.counter.key_count

    def tearDown(self):
        # Reset count value
        self.counter.key_count = self.init_count
        self.counter.stop()
        del self.counter

    def test_init(self):
        self.assertEqual(
            self.counter.key_count,
            self.init_count,
            'Init count should be read from storage'
        )

    def test_save_load(self):
        init_count_backup = self.init_count

        self.counter.update_count()
        last_count = self.counter.key_count
        self.counter.stop()

        self.setUp()
        self.assertEqual(
            self.counter.key_count,
            last_count,
            'Should load count from storage upon start up'
        )

        self.init_count = init_count_backup

    def test_daily_reset(self):
        pass

    def test_handle_keyevent(self):
        start_count = self.counter.key_count
        self.counter.handle_keyevent(None)
        self.assertEqual(
            self.counter.key_count,
            start_count + 1,
            'Count should increase by 1 by calling .handle_keyevent once'
        )

    def test_update_count(self):
        start_count = self.counter.key_count
        self.counter.update_count()
        self.assertEqual(
            self.counter.key_count,
            start_count + 1,
            'Count should increase by 1 by calling .update_count once'
        )


if __name__ == '__main__':
    unittest.main()
