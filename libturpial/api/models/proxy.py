# -*- coding: utf-8 -*-

""" Module to handle proxies information """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 12, 2011

class Proxy:
    def __init__(self):
        self.secure = False
        self.server = ''
        self.port = ''
        self.username = ''
        self.password = ''
