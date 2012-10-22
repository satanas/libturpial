# -*- coding: utf-8 -*-

""" Module to handle lastest trends """
#
# Author: Wil Alvarez (aka Satanas)
# Jul 20, 2011


class TrendsResults:
    def __init__(self):
        self.title = None
        self.timestamp = None
        self.items = None


class Trend:
    def __init__(self):
        self.name = None
        self.promoted = None
