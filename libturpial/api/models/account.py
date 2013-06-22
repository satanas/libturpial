# -*- coding: utf-8 -*-

from libturpial.config import AccountConfig
from libturpial.api.models.column import Column
from libturpial.api.models.profile import Profile
from libturpial.lib.protocols.twitter import twitter
from libturpial.lib.protocols.identica import identica
from libturpial.lib.interfaces.protocol import Protocol

from libturpial.common import *
from libturpial.exceptions import EmptyOAuthCredentials, \
        EmptyBasicCredentials, ErrorLoadingAccount


class Account(object):
    # TODO: Update doc
    """
    This class holds all related methods to an user account. It contains a
    protocol instance associated to the user and the profile model to store the
    user details. This is the class you must instanciate if you want to handle
    a user account.

    Account let you perform two main actions: create a new account or load an
    existing one. To create a new valid account based on OAuth authentication
    do the following:

    >>> account = Account.new_oauth('twitter', 'my_user', 'key', 'secret', 'verifier')

    And to create a new one for Basic authentication:

    >>> account = Account.new_basic('identica', 'my_user', 'my_password')

    Both commands will create a new entry in *~/.config/turpial/accounts/*
    with all the information about configuration. An existing account can be
    loaded later only with the account id. For example:

    >>> account = Account.load('my_user-twitter')

    Or

    >>> account = Account.load('my_user-identica')

    From this point you can use the method described here to handle the
    *account* object.
    """

    def __init__(self, protocol_id, username=None):
        self.config = None
        self.protocol_id = protocol_id

        if username:
            self.__setup(username)

        self.columns = []
        self.profile = None
        self.friends = None
        self.lists = None

        if self.protocol_id == Protocol.TWITTER:
            self.protocol = twitter.Main()
        elif self.protocol_id == Protocol.IDENTICA:
            self.protocol = identica.Main()

    def __setup(self, username):
        self.id_ = build_account_id(username, self.protocol_id)
        self.username = username

    @staticmethod
    def new(protocol_id, username=None):
        # TODO: Update doc
        """
        Return a new account object based on OAuth authentication. This will
        create a new entry in *~/.config/turpial/accounts/* with all the
        configuration stuff. It needs the *username*, the OAuth *key*, the OAuth
        *secret* and the *verifier* (also known as PIN) given by the service.

        If the account exists this method overwrite the previous credentials
        """
        account = Account(protocol_id, username)
        return account

    @staticmethod
    def new_from_params(protocol_id, username, key, secret, verifier):
        # TODO: Update doc, new methods do not do the fetch automatically
        """
        Return a new account object based on OAuth authentication. This will
        create a new entry in *~/.config/turpial/accounts/* with all the
        configuration stuff. It needs the *username*, the OAuth *key*, the OAuth
        *secret* and the *verifier* (also known as PIN) given by the service.

        If the account exists this method overwrite the previous credentials
        """
        account = Account(protocol_id, username)
        account.setup_user_credentials(account.id_, key, secret, verifier)
        return account

    @staticmethod
    def load(account_id):
        """
        Return the Account object associated to *account_id* loaded from
        existing configuration. If the *account_id* does not correspond to a
        valid account returns a
        :class:`libturpial.exceptions.ErrorLoadingAccount` exception.
        If credentials in configuration file are empty it returns a 
        :class:`libturpial.exceptions.EmptyOAuthCredentials` or a
        :class:`libturpial.exceptions.EmptyBasicCredentials` exception.
        """
        if not AccountConfig.exists(account_id):
            raise ErrorLoadingAccount("Account has no stored credentials")

        username = get_username_from(account_id)
        protocol_id = get_protocol_from(account_id)

        account = Account.new(protocol_id, username)
        account.config = AccountConfig(account_id)
        key, secret, verifier = account.config.load_oauth_credentials()
        account.setup_user_credentials(account.id_, key, secret, verifier)
        account.fetch()
        return account

    def request_oauth_access(self):
        return self.protocol.request_token()

    def authorize_oauth_access(self, pin):
        profile = self.protocol.authorize_token(pin)
        self.__setup(profile.username)

    def save(self):
        self.config = AccountConfig(self.id_)
        token = self.get_oauth_token()
        if token:
            self.config.save_oauth_credentials(token.key, token.secret, token.verifier)

    def fetch(self):
        self.profile = self.protocol.verify_credentials()
        self.lists = self.protocol.get_lists(self.profile.username)

        self.columns = [
            Column(self.id_, ColumnType.TIMELINE),
            Column(self.id_, ColumnType.REPLIES),
            Column(self.id_, ColumnType.DIRECTS),
            Column(self.id_, ColumnType.SENT),
            Column(self.id_, ColumnType.FAVORITES)] + self.lists
        return self.id_

    def get_friends(self):
        self.friends = self.protocol.get_following(only_id=True)
        return self.friends

    def get_columns(self):
        return self.columns

    def get_list_id(self, list_name):
        for li in self.lists:
            if li.name == list_name:
                return li.id_
        return None

    def purge_config(self):
        """
        Delete all config files related to this account
        """
        self.config.dismiss()

    def delete_cache(self):
        """
        Clean cache associated to this account
        """
        self.config.delete_cache()

    def get_cache_size(self):
        """
        Return disk space used by cache in bytes
        """
        return self.config.calculate_cache_size()

    def is_authenticated(self):
        """
        Return `True` if the current account has been logged in, `False`
        otherwise
        """
        return self.config != None and self.profile != None

    def update_profile(self, fullname=None, url=None, bio=None, location=None):
        self.profile = self.protocol.update_profile(fullname, url, bio, location)
        return self.profile

    def __getattr__(self, name):
        try:
            return getattr(self.protocol, name)
        except:
            try:
                return getattr(self.profile, name)
            except:
                raise AttributeError
