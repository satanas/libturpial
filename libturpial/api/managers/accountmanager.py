# -*- coding: utf-8 -*-


import logging

from libturpial.common import LoginStatus, build_account_id
from libturpial.lib.config import AccountConfig
from libturpial.api.models.account import Account
from libturpial.common.exceptions import ErrorCreatingAccount, \
        ErrorLoadingAccount, AccountNotLoggedIn


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
        # TODO: Set the timeout
        #timeout = int(self.config.read('Advanced', 'socket-timeout'))
        #self.protocol.timeout = timeout

        self.__accounts[account_id] = Account.load(account_id)
        self.log.debug('Account %s loaded successfully' % account_id)
        return account_id

    def register_oauth_account(self, protocol_id, username, key, secret, verifier):
        if username == '' or protocol_id == '':
            raise ErrorCreatingAccount

        account_id = build_account_id(username, protocol_id)
        if account_id in self.__accounts:
            self.log.debug('Account %s is already registered' % account_id)
        else:
            account = Account.new_oauth(protocol_id, username, key, secret, verifier)
            self.__accounts[account_id] = account
            self.log.debug('Account %s registered successfully' % account_id)
        return account_id

    def register_basic_account(self, protocol_id, username, password):
        if username == '' or protocol_id == '':
            raise ErrorCreatingAccount

        account_id = build_account_id(username, protocol_id)
        if account_id in self.__accounts:
            self.log.debug('Account %s is already registered' % account_id)
        else:
            account = Account.new_basic(protocol_id, username, password)
            self.__accounts[account_id] = account
            self.log.debug('Account %s registered successfully' % account_id)
        return account_id

    def unregister(self, account_id, delete_all):
        if account_id in self.__accounts:
            self.__accounts[account_id].remove(delete_all)
            del self.__accounts[account_id]
        else:
            self.log.debug('Account %s is not registered' % account_id)

    def login_status(self, account_id, status):
        if account_id in self.__accounts:
            self.__accounts[account_id].logged_in = status
        else:
            self.log.debug('Account %s is not registered' % account_id)

    def get(self, account_id, validate_login=False):
        """
        Return the :class:`libturpial.api.models.account.Account` object
        associated to *account_id* if it has been loaded or try to load the
        account otherwise. If any of the previous method fails it raise an
        :class:`libturpial.common.exceptions.ErrorLoadingAccount` exception.
        """
        try:
            account = self.__accounts[account_id]
        except KeyError:
            self.load(account_id)
            account = self.__accounts[account_id]

        if validate_login and account.logged_in != LoginStatus.DONE:
            raise AccountNotLoggedIn

        return account

    def list(self):
        """
        Return an alphabetically sorted list with all account ids registered
        """
        return sorted(self.__accounts.keys())

    def get_all(self):
        """
        Return all :class:`libturpial.api.models.account.Account` objects
        registered
        """
        return self.__accounts.values()
