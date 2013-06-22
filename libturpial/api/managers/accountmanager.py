# -*- coding: utf-8 -*-

from libturpial.common import build_account_id
from libturpial.api.models.account import Account
from libturpial.exceptions import ErrorCreatingAccount, \
        ErrorLoadingAccount, AccountNotAuthenticated, \
        AccountAlreadyRegistered


class AccountManager:
    def __init__(self, config):
        self.config = config
        self.__accounts = {}
        self.__load_registered()

    def __len__(self):
        return len(self.__accounts)

    def __iter__(self):
        return self.__accounts.iteritems()

    def __load_registered(self):
        accounts = self.config.get_stored_accounts()
        for account_id in accounts:
            self.load(account_id)

    def load(self, account_id):
        # TODO: Set the timeout
        #timeout = int(self.config.read('Advanced', 'socket-timeout'))
        #self.protocol.timeout = timeout

        self.__accounts[account_id] = Account.load(account_id)
        return self.__accounts[account_id]

    def register(self, account):
        # TODO: Update doc
        """
        Register a new OAuth based account in libturpial record for the protocol
        specified by *protocol_id*, *username* and OAuth params: *key*,
        *secret* and *verifier*. Return the id of the new account if the
        registration process was successful, otherwise raise an
        :class:`libturpial.common.exceptions.ErrorCreatingAccount` exception.
        """
        if not account.is_authenticated():
            raise AccountNotAuthenticated

        if account.id_ in self.__accounts:
            raise AccountAlreadyRegistered
        else:
            self.__accounts[account.id_] = account
            account.save()
        return account.id_

    def unregister(self, account_id, delete_all):
        """
        Remove the account *account_id* from libturpial record. If *delete_all*
        is **True** all configuration files are deleted from disk. Be careful
        because this operation can not be undone.
        """
        if account_id in self.__accounts:
            if delete_all:
                self.__accounts[account_id].purge_config()
            del self.__accounts[account_id]
            return account_id
        return None

    def get(self, account_id, validate_login=False):
        """
        Return the :class:`libturpial.api.models.account.Account` object
        associated to *account_id* if it has been loaded or try to load the
        account otherwise. If any of the previous method fails it raise an
        :class:`libturpial.exceptions.ErrorLoadingAccount` exception.
        If *validate_login* is **True** and the account is not logged in a
        :class:`libturpial.common.exceptions.AccountNotLoggedIn` exception is
        raised.
        """
        try:
            account = self.__accounts[account_id]
        except KeyError:
            self.load(account_id)
            account = self.__accounts[account_id]

        if validate_login and account.is_not_logged_in():
            raise AccountNotLoggedIn

        return account

    def list(self):
        """
        Return an alphabetically sorted list with all account ids registered
        """
        return sorted(self.__accounts.keys())

    def accounts(self):
        """
        Return all :class:`libturpial.api.models.account.Account` objects
        registered
        """
        return self.__accounts.values()
