#!/usr/bin/env python
'''
File name:          server.py
Author:             Dikke Neef
Date created:       28/8/2017
Date last modified: 30/8/2017
Python Version:     2.7.13
'''
#==============================================================================
import zerorpc
import json

def stringify(d):
    return json.dumps(d)

class HelloRPC(object):
    def hello(self, name):
        print("Yarrr, Python Server is responding!")
        return "Hello, %s" % name

def main():
    s = zerorpc.Server(HelloRPC())
    s.bind("tcp://0.0.0.0:4242")
    s.run()

if __name__ == '__main__':
    main()