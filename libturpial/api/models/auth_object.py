# -*- coding: utf-8 -*-

""" Module to handle auth objects """
#
# Author: Wil Alvarez (aka Satanas)
# Oct 05, 2011

class AuthObject:
    def __init__(self, type_, token=None, url=None):
        self.type_ = type_
        self.token = token
        self.url = url
    
    def must_auth(self):
        ''' Test if token must be authenticated '''
        if self.type_ == 'auth':
            return True
        return False
