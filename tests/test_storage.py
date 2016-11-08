#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from io import open
import random
import unittest
import sys

if sys.version_info.major < 3:
    from backports import csv
else:
    import csv

import tinydb

from keycounter.storage import CountDataStorage


class CountDataStorageTest(unittest.TestCase):

    def setUp(self):
        # Use 7 days in the future for testing
        self.date = datetime.now() + timedelta(7)
        self.format = '%Y/%m/%d'
        self.store = CountDataStorage()

    def tearDown(self):
        # Delete test record from database
        db = self.store._CountDataStorage__db
        Day = tinydb.Query()
        record = db.get(Day.Date == self.date.strftime(self.format))
        if record is not None:
            db.remove(eids=[record.eid, ])
            # Cleanup exported CSV file
            self.store.export()
        del self.store

    def test_load_save(self):
        self.assertEqual(
            self.store.get(self.date),
            0,
            'Count for non-existing day should be 0'
        )
        count = random.randint(1, 10000)
        self.store.save(self.date, count)
        self.setUp()
        self.assertEqual(
            self.store.get(self.date),
            count,
            'Loaded count should be {}'.format(count)
        )

    def test_export(self):
        self.store.export()
        csv_fpath = self.store._CountDataStorage__csv_location
        with open(csv_fpath, newline='', encoding='utf-8') as rf:
            reader = csv.DictReader(rf)
            for row in reader:
                day = datetime.strptime(row['Date'], self.format)
                self.assertEqual(
                    self.store.get(day),
                    int(row['Count']),
                    'Count of date {} should be {}'.format(
                        row['Date'],
                        row['Count']
                    )
                )


if __name__ == '__main__':
    unittest.main()
