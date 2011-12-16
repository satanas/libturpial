# -*- coding: utf-8 -*-

""" Module to handle core responses """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 13, 2011

from libturpial.common import ERROR_CODES

class Response:
    def __init__(self, items=None, code=0, account_id=None):
        self.code = code
        self.account_id = account_id
        if code > 0:
            self.errmsg = ERROR_CODES[code]
        else:
            self.errmsg = ''
        
        if not items:
            self.items = []
        else:
            self.items = items
        
    def __getitem__(self, key):
        return self.items[key]
        
    def __len__(self):
        return len(self.items)
    
    def add(self, item):
        self.items.append(item)
