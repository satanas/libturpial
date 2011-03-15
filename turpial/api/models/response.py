# -*- coding: utf-8 -*-

""" Module to handle core responses """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 13, 2011

class Response:
    ERROR_CODES = {
        666: 'Error del orto'
    }
    
    def __init__(self, items=None, code=0):
        self.code = code
        
        if code > 0:
            self.errmsg = ERROR_CODES[code]
        else:
            self.errmsg = ''
        
        if not items:
            self.items = []
        else:
            self.items = items
        
    def add(self, item):
        self.items.append(item)
