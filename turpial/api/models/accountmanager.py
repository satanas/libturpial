# -*- coding: utf-8 -*-

""" Module to handle multiples accounts """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 13, 2011

import logging

from turpial.api.models.account import Account

class AccountManager:
    def __init__(self):
        self.log = logging.getLogger('AccountManager')
        self.log.debug('Started')
        self.__accounts = {}
        
    def __len__(self):
        return len(self.__accounts)
        
    def __iter__(self):
        return self.__accounts.iteritems()
        
    def register(self, username, password, protocol_id):
        account_id = "%s-%s" % (username, protocol_id)
        if self.__accounts.has_key(account_id):
            self.log.debug('Account %s is already registered' % account_id)
        else:
            account = Account(username, password, account_id, protocol_id)
            self.__accounts[account_id] = account
        
    def unregister(self, account_id):
        if self.__accounts.has_key(account_id):
            del self.__accounts[account_id]
        else:
            self.log.debug('Account %s is not registered' % account_id)
            
    def get(self, account_id):
        return self.__accounts[account_id]
        
    def list(self):
        return self.__accounts.iterkeys()
