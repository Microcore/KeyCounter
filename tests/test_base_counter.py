#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import unittest

from keycounter.base_counter import BaseKeyCounter
from keycounter.storage import CountDataStorage


class BaseKeyCounterTest(unittest.TestCase):
    '''Unit test for BaseKeyCounter class'''

    def setUp(self):
        self.counter = BaseKeyCounter()
        self.counter.update_ui = lambda: None
        # We'll reset the count to init value so we don't mess up real data
        self.init_count = self.counter.key_count

    def tearDown(self):
        # Reset count value
        self.counter.key_count = self.init_count
        self.counter.stop()
        del self.counter

    def test_init(self):
        self.counter.start()
        self.assertEqual(
            self.counter.key_count,
            self.init_count,
            'Init count should be read from storage'
        )

    def test_save_load(self):
        self.counter.start()
        init_count_backup = self.init_count

        self.counter.update_count()
        last_count = self.counter.key_count
        self.counter.stop()

        self.setUp()
        self.counter.start()
        self.assertEqual(
            self.counter.key_count,
            last_count,
            'Should load count from storage upon start up'
        )

        self.init_count = init_count_backup

    def test_daily_reset(self):
        self.assertTrue(
            self.counter.daily_reset,
            'BaseKeyCounter.daily_reset should be True'
        )
        # Set `today` to yesterday and manually trigger daily reset
        yesterday = datetime.now() + timedelta(-1)
        self.counter.today = yesterday
        self.counter.start()
        yesterday_count_backup = self.counter.key_count

        self.counter.handle_keyevent(None)
        self.assertEquals(
            self.counter.key_count,
            1,
            'Count should be 1 after a daily reset'
        )
        self.assertEqual(
            self.counter.today.day,
            datetime.now().day,
            'BaseKeyCounter.today should update after a daily reset'
        )
        self.assertEqual(
            yesterday_count_backup,
            self.counter.storage.get(yesterday),
            'Count of the last day should be saved'
        )

        # Restore count of yesterday so we don't mess up real data
        self.counter.today = yesterday
        self.counter.key_count = yesterday_count_backup

    def test_handle_keyevent(self):
        self.counter.start()
        start_count = self.counter.key_count
        self.counter.handle_keyevent(None)
        self.assertEqual(
            self.counter.key_count,
            start_count + 1,
            'Count should increase by 1 by calling .handle_keyevent once'
        )

    def test_update_count(self):
        self.counter.start()
        start_count = self.counter.key_count
        self.counter.update_count()
        self.assertEqual(
            self.counter.key_count,
            start_count + 1,
            'Count should increase by 1 by calling .update_count once'
        )

    def test_save_load_config(self):
        self.assertRaises(
            NotImplementedError,
            self.counter.load_config
        )
        self.assertRaises(
            NotImplementedError,
            self.counter.save_config
        )

    def test_storage(self):
        self.counter.setup_storage()
        self.assertIsInstance(
            self.counter.storage,
            CountDataStorage,
            'BaseKeyCounter.storage should be an instance of CountDataStorage'
        )

    def test_log(self):
        self.counter.log('BaseKeyCounter.log should log without %s', 'error')

if __name__ == '__main__':
    unittest.main()
