#!/usr/bin/env python
"""
File name:          server.py
Author:             Dikke Neef
Date created:       28/08/2017
Date last modified: 01/09/2017
Python Version:     2.7.13
"""
# ==============================================================================
from functools import partial
import threading
import schedule
import zerorpc
import json
import time

try:
    import cPickle as pickle
except ImportError:
    import pickle


class Scheduler(object):
    def __init__(self, fnc, interval=2):
        self.fnc = fnc
        self.interval = interval
        thread = threading.Thread(target=self.run)
        thread.daemon = False
        thread.start()

    def run(self):
        schedule.every(self.interval).seconds.do(self.fnc)
        while True:
            schedule.run_pending()
            time.sleep(1)


def stringify(d):
    return json.dumps(d)


def save_object(obj, fn='zerorpc'):
    print("saving")
    with open(fn + '.db', 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def open_object(fn='zerorpc'):
    return pickle.load(open(fn + '.db', "rb"))


class HumongousTools(object):
    def __init__(self):
        self.scheduler = None

    def backup(self):
        self.scheduler = Scheduler(partial(save_object, self))

    def hello(self, name):
        return "Hello, " + name


def main():
    reload_server = True
    server = HumongousTools()
    if not reload_server: server = open_object()

    server.backup()
    s = zerorpc.Server(server)
    s.bind("tcp://0.0.0.0:4242")
    s.run()

if __name__ == '__main__':
    main()
