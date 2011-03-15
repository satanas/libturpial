# -*- coding: utf-8 -*-

""" Module to handle core responses """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 13, 2011

class Response:
    ERROR_CODES = {
        401: 'Unauthorized credentials',
        402: 'Status duplicated',
        403: 'Already friend',
        404: 'Invalid request',
        405: 'Already requested to follow',
        406: 'Rate Limit',
        407: 'Invalid search',
        408: 'Too long search',
        409: 'Invalid account',
        410: 'Invalid column',
        
        500: 'Internal server error',
        501: 'Not implemented',
        502: 'Service down',
        503: 'Service overloaded',
        504: 'Server timeout',
        505: 'Can\'t connect to server',
        
        999: 'Unknown error',
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
