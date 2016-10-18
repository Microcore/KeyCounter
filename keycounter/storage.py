#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
The storage abstraction layer.
Currently using TinyDB as actual storage, and exports to a CSV file.
'''

import os.path
import platform
import sys

if sys.version_info.major < 3:
    from backports import csv
else:
    import csv

import tinydb


class CountDataStorage(object):

    __date_format = '%Y/%m/%d'
    __csv_fields = ('Date', 'Count', )

    def __init__(self):
        super(CountDataStorage, self).__init__()
        self.__detect_location()
        self.__setup_database()

    def __detect_location(self):
        '''Detect platform specific database file location'''
        if platform.system() == 'Windows':
            import win32com.client
            _ws = win32com.client.Dispatch('Wscript.Shell')
            data_dir = os.path.join(
                _ws.SpecialFolders('MyDocuments'), 'KeyCounter'
            )
            del _ws
        elif platform.system() == 'Darwin':
            data_dir = os.path.expanduser('~/Documents/KeyCounter')
        else:
            raise NotImplementedError(
                u'System {} is currently not supported'.format(
                    platform.system()
                )
            )

        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
        self.__db_location = os.path.join(data_dir, 'database.db')
        self.__csv_location = os.path.join(data_dir, 'data_export.csv')

    def __setup_database(self):
        '''Setup the real storage system'''
        self.__db = tinydb.TinyDB(self.__db_location)

    def save(self, day, count):
        '''
        Save count for given day.
        Args:
          - day: <datetime>
          - count: <int>
        Returns: None
        '''
        date = day.strftime(self.__date_format)
        count = int(count)
        Day = tinydb.Query()

        if self.__db.contains(Day.Date == date):
            self.__db.update({'Count': count}, Day.Date == date)
        else:
            self.__db.insert({'Date': date, 'Count': count})

    def get(self, day):
        '''
        Get count for given day.
        Args:
          - day: <datetime>
        Returns: <int> count
        '''
        date = day.strftime(self.__date_format)
        Day = tinydb.Query()
        record = self.__db.get(Day.Date == date)
        if record is None:
            return 0
        return record['Count']

    def export(self):
        '''
        Export all data into a CSV file. Will overwrite existing file.
        '''
        with open(self.__csv_location, 'w') as wf:
            writer = csv.DictWriter(wf, self.__csv_fields)
            writer.writeheader()
            for day in self.__db.all():
                writer.writerow(day)
