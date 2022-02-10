# -*- coding: utf-8 -*-

from libturpial.api.models.account import Account
from libturpial.exceptions import AccountNotAuthenticated, AccountAlreadyRegistered


class AccountManager:
    """
    This class has methods to manage accounts. You can register new accounts,
    load and unregister existing accounts.

    This manager can be iterated and each element will have the account id
    and the respective object. For example:

    >>> from libturpial.config import AppConfig
    >>> config = AppConfig()
    >>> account_manager = AccountManager(config)
    >>> [item for item in account_manager]

    To check how much accounts are registered simply use the `len` function:

    >>> len(accman)
    2
    """
    def __init__(self, config, load=True):
        self.config = config
        self.__accounts = {}
        if load:
            self.__load_registered()

    def __len__(self):
        return len(self.__accounts)

    def __iter__(self):
        return iter(self.__accounts.items())

    def __load_registered(self):
        accounts = self.config.get_stored_accounts()
        for account_id in accounts:
            self.load(account_id)

    def load(self, account_id):
        """
        Load and existing account identified by *account_id*. If the load
        fails an :class:`libturpial.exceptions.ErrorLoadingAccount` exception
        will raise. Return the id of the account loaded on success
        """
        # TODO: Set the timeout
        # timeout = int(self.config.read('Advanced', 'socket-timeout'))
        # self.protocol.timeout = timeout

        self.__accounts[account_id] = Account.load(account_id)
        return account_id

    def register(self, account):
        """
        Register the *account* object passed as argument. If the account hasn't
        been authenticated it will raise a
        :class:`libturpial.exceptions.AccountNotAuthenticated` exception. If
        the account is already registered a
        :class:`libturpial.exceptions.AccountAlreadyRegistered` exception will
        raise. Return the id of the account registered on success
        """
        if not account.is_authenticated():
            raise AccountNotAuthenticated

        if account.id_ in self.__accounts:
            raise AccountAlreadyRegistered
        else:
            account.save()
            self.load(account.id_)

        return account.id_

    def unregister(self, account_id, delete_all):
        """
        Remove the account identified by *account_id* from memory. If *delete_all*
        is `True` all configuration files are deleted from disk. Be careful
        because this operation can not be undone. Return the id of the
        unregistered column on success, `None` otherwise
        """
        if account_id in self.__accounts:
            if delete_all:
                self.__accounts[account_id].purge_config()
            del self.__accounts[account_id]
            return account_id
        return None

    def get(self, account_id):
        """
        Obtain the account identified by *account_id*. If the account is not
        loaded yet, it will be loaded immediately. Return a
        :class:`libturpial.api.models.account.Account` object on success
        """
        try:
            account = self.__accounts[account_id]
        except KeyError:
            self.load(account_id)
            account = self.__accounts[account_id]

        return account

    def list(self):
        """
        Return an alphabetically sorted list with all the ids of the registered
        accounts.
        """
        return sorted(self.__accounts.keys())

    def accounts(self):
        """
        Return a list of :class:`libturpial.api.models.account.Account` objects
        with all the accounts registered
        """
        return list(self.__accounts.values())
