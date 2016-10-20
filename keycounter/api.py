#!/usr/bin/env python
# -*- coding: utf-8 -*-
from multiprocessing.connection import Listener
import threading


class CountApiServer(threading.Thread):

    def __init__(self, port, parent):
        super(CountApiServer, self).__init__()

        self.parent = parent
        self.__listener = Listener(('127.0.0.1', port))

    def run(self):
        conn = self.__listener.accept()
        while 1:
            if conn.closed:
                conn = self.__listener.accept()
            try:
                msg = conn.recv()
            except EOFError:
                conn.close()
                continue
            else:
                if msg == 'quit':
                    conn.close()
                    break
            conn.send(self.parent.key_count)
        self.__listener.close()
        self.parent.stop()
