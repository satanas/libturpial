# -*- coding: utf-8 -*-

""" Module to handle multiples accounts """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 13, 2011

import logging

from libturpial.common import *
from libturpial.config import AccountConfig
from libturpial.api.models.account import Account

class AccountManager:
    def __init__(self, config):
        self.log = logging.getLogger('AccountManager')
        self.log.debug('Started')
        self.config = config
        self.__accounts = {}

    def __len__(self):
        return len(self.__accounts)

    def __iter__(self):
        return self.__accounts.iteritems()

    def load(self, account_id):
        cfg = AccountConfig(account_id)
        auth = cfg.read_section('OAuth')
        username = cfg.read('Login', 'username')
        protocol = cfg.read('Login', 'protocol')
        p = cfg.revert(cfg.read('Login', 'password'), username)

        if self.__accounts.has_key(account_id):
            self.log.debug('Account %s is already registered' % account_id)
        else:
            account = Account(username, account_id, protocol, p, auth, cfg)
            timeout = int(self.config.read('Advanced', 'socket-timeout'))
            account.protocol.timeout = timeout
            self.log.debug('Using %i sec for socket timeout in account %s' % (
                account.protocol.timeout, account_id))
            self.__accounts[account_id] = account
            self.log.debug('Account %s loaded successfully' % account_id)
        return account_id

    def change_id(self, original_id, destination_id):
        account = self.get(original_id)
        new_id = "%s-%s" % (destination_id, account.protocol_id)
        self.unregister(original_id, True)
        account.username = destination_id
        account.profile.username = destination_id
        account.config = AccountConfig(new_id, "")
        account.store_token()
        account.id_ = new_id
        self.__accounts[new_id] = account
        return new_id

    def register(self, username, protocol_id, passwd, auth):
        if username == '' or protocol_id == '':
            return None

        account_id = "%s-%s" % (username, protocol_id)
        if self.__accounts.has_key(account_id):
            self.log.debug('Account %s is already registered' % account_id)
            self.__accounts[account_id].update(passwd)
        else:
            account = Account(username, account_id, protocol_id, passwd, auth)
            timeout = int(self.config.read('Advanced', 'socket-timeout'))
            account.protocol.timeout = timeout
            self.log.debug('Using %i sec for socket timeout in account %s' % (
                account.protocol.timeout, account_id))
            self.__accounts[account_id] = account
            self.log.debug('Account %s registered successfully' % account_id)
        return account_id

    def unregister(self, account_id, delete_all):
        if self.__accounts.has_key(account_id):
            self.__accounts[account_id].remove(delete_all)
            del self.__accounts[account_id]
        else:
            self.log.debug('Account %s is not registered' % account_id)

    def login_status(self, account_id, status):
        if self.__accounts.has_key(account_id):
            self.__accounts[account_id].logged_in = status
        else:
            self.log.debug('Account %s is not registered' % account_id)

    def get(self, account_id, validate_login=True):
        account = self.__accounts[account_id]
        if (validate_login and account.logged_in == LoginStatus.DONE) or (not validate_login):
            return account
        else:
            raise ZeroDivisionError

    def list(self):
        temp = self.__accounts.keys()
        temp.sort()
        return temp

    def get_all(self):
        return self.__accounts.values()

