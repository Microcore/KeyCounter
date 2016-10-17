#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from io import open
import logging
import os.path
import sys

if sys.version_info.major < 3:
    from backports import csv
else:
    import csv


class BaseKeyCounter(object):
    '''Base skeleton for a KeyCounter instance'''

    name = 'KeyCounter'

    csv_file = None  # Should be implemented in subclass
    __csv_fields = ('Date', 'Count', )
    __date_format = '%Y/%m/%d'

    def __init__(self):
        '''
        Init the counter.
        - Load config
        - Setup UI
        - Start event loop
        '''
        self.key_count = 0
        self.daily_reset = False

        self.today = datetime.now().day
        self.check_storage()

    def check_storage(self):
        if not os.path.exists(os.path.dirname(self.csv_data_file)):
            self.log(
                'Making data storage %s', os.path.dirname(self.csv_data_file)
            )
            os.makedirs(os.path.dirname(self.csv_data_file))
        if not os.path.isfile(self.csv_data_file):
            self.log('Creating empty CSV data file %s', self.csv_data_file)
            with open(self.csv_data_file, 'w') as wf:
                writer = csv.DictWriter(wf, self.__csv_fields)
                writer.writeheader()

    @property
    def csv_data_file(self):
        if self.csv_file is not None:
            return self.csv_file
        raise NotImplementedError(u'Should be implemented in subclass')

    def log(self, *args, **kwargs):
        '''Logging'''
        logging.debug(*args, **kwargs)

    def load_config(self):
        '''Load configuration from storage'''
        raise NotImplementedError(u'Should be implemented in subclass')

    def save_config(self):
        '''Save configuration to storage'''
        raise NotImplementedError(u'Should be implemented in subclass')

    def start(self):
        '''Start the event loop'''
        raise NotImplementedError(u'Should be implemented in subclass')

    def stop(self):
        '''Stop the event loop and save current count'''
        raise NotImplementedError(u'Should be implemented in subclass')

    def do_daily_reset(self):
        '''Reset count and start a new day'''
        self.log('Perform daily reset')
        yesterday_count = self.key_count - 1
        yesterday = datetime.now() - timedelta(1)
        self.save_data(yesterday, yesterday_count)
        self.key_count -= yesterday_count
        if self.key_count < 0:
            self.key_count = 0
        self.update_ui()

    def load_data(self, day):
        '''Load count data for specific day'''
        self.check_storage()
        day_value = day.strftime(self.__date_format)
        self.log(
            'Loading data for %s from %s', day_value, self.csv_data_file
        )
        with open(self.csv_data_file) as rf:
            reader = csv.DictReader(rf, self.__csv_fields)
            for row in reader:
                if row['Date'] == day_value:
                    # Count is type `int`
                    return int(row['Count'])
        return 0

    def save_data(self, day, count):
        '''Save count data for specific day'''
        self.check_storage()
        day_value = day.strftime(self.__date_format)

        self.log(
            'Saving data for %s into %s', day_value, self.csv_data_file
        )
        # FIXME Update row for specified day instead of rewriting the whole file
        with open(self.csv_data_file, 'w') as wf:
            writer = csv.DictWriter(wf, self.__csv_fields)
            writer.writerow({'Date': day_value, 'Count': count})

    def check_daily_reset(self):
        '''Check whether it's time to do daily reset'''
        now = datetime.now()
        if now.day != self.today:
            self.do_daily_reset()
            self.today = now.day

    def update_count(self):
        '''Update count and reflect the change to UI'''
        self.key_count += 1
        self.update_ui()

    def update_ui(self):
        '''Update user interface'''
        raise NotImplementedError(u'Should be implemented in subclass')

    def handle_keyevent(self, _):
        '''
        Handle key event, properly change count and UI.
        This method should be properly registered to OS's KeyUp event.
        '''
        self.update_count()
        if self.daily_reset:
            self.check_daily_reset()
