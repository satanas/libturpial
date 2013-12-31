# -*- coding: utf-8 -*-

from libturpial.config import AccountConfig
from libturpial.api.models.column import Column
from libturpial.api.models.profile import Profile
from libturpial.lib.protocols.twitter import twitter
from libturpial.lib.protocols.identica import identica
from libturpial.lib.interfaces.protocol import Protocol

from libturpial.common import *
from libturpial.exceptions import EmptyOAuthCredentials, \
        EmptyBasicCredentials, ErrorLoadingAccount, \
        AccountNotAuthenticated


class Account(object):
    """
    This class represents an user account and holds all it related methods.
    This is done thanks to one :class:`libturpial.lib.interfaces.protocol.Protocol` 
    instance associated to the user account that handles all the dirty work 
    against the service (Twitter, Identi.ca, etc) as well as one 
    :class:`libturpial.api.models.profile.Profile` model that store the user 
    details.

    This is the class you must instanciate if you want to handle/authenticate 
    a user account.

    *Account* let you perform three actions to build an account: create a new 
    account from scratch, create a new account from params and load a
    previously registered account. To create a new account from scratch do:

    >>> account = Account.new('twitter')

    If you know the username too, then you can pass it as argument:

    >>> account = Account.new('twitter', 'username')

    At this point, that account is not a valid account yet because it 
    hasn't been authenticated. You should do the authentication by yourself.
    This is, request OAuth access:

    >>> url = account.request_oauth_access()

    That method will return an URL that your user must visit to authorize the 
    app. After that, you must to ask for the PIN returned by the service and
    execute:

    >>> account.authorize_oauth_access('the_pin')

    And voilá! You now have a valid and fully authenticated account ready to be
    registered in :class:`libturpial.api.core.Core`.

    But *Account* let you create accounts passing all the params needed for
    the OAuth authentication. If you already know those params (user key, 
    user secret and PIN) then you just need to execute:

    >>> account = Account.new_from_params('twitter', 'username', 'key', 'secret', 'the_pin')

    And you will have a valid and fully authenticated account ready to be
    registered in :class:`libturpial.api.core.Core` too.

    Now, what if you did all this process before and registered the account
    in :class:`libturpial.api.core.Core`? Well, you just need to load the
    account then:

    >>> account = Account.load('username-twitter')

    And you will have an account already authenticated and ready to be used.

    From this point you can use the method described here to handle the
    account object.
    """

    def __init__(self, protocol_id, username=None):
        self.id_ = None
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

    def __repr__(self):
        return "libturpial.api.models.Account %s-%s" % (self.username, self.protocol_id)

    def __setup(self, username):
        self.id_ = build_account_id(username, self.protocol_id)
        self.username = username

    @staticmethod
    def new(protocol_id, username=None):
        """
        Return a new account object associated to the protocol identified by
        *protocol_id*. If *username* is not None it will build the account_id 
        for the account.

        This account is empty and must be authenticated before it can be registered
        in :class:`libturpial.api.core.Core`.

        .. warning::
            None information is stored at disk at this point.
        """
        account = Account(protocol_id, username)
        return account

    @staticmethod
    def new_from_params(protocol_id, username, key, secret, verifier):
        """
        Return a new account object associated to the protocol identified by
        *protocol_id* and authenticated against the respective service (Twitter,
        Identi.ca, etc) using *username*, *key*, *secret* and *verifier* (aka 
        PIN).

        This account is authenticated after creation, so it can be registered
        in :class:`libturpial.api.core.Core` immediately.

        .. warning::
            None information is stored at disk at this point.
        """
        account = Account(protocol_id, username)
        account.setup_user_credentials(account.id_, key, secret)
        return account

    @staticmethod
    def load(account_id):
        """
        Return the account object associated to *account_id* loaded from
        existing configuration. If the *account_id* does not correspond to a
        valid account it returns a
        :class:`libturpial.exceptions.ErrorLoadingAccount` exception.

        If credentials in configuration file are empty it returns a 
        :class:`libturpial.exceptions.EmptyOAuthCredentials` exception.
        """
        if not AccountConfig.exists(account_id):
            raise ErrorLoadingAccount("Account has no stored credentials")

        username = get_username_from(account_id)
        protocol_id = get_protocol_from(account_id)

        account = Account.new(protocol_id, username)
        account.config = AccountConfig(account_id)
        key, secret = account.config.load_oauth_credentials()
        account.setup_user_credentials(account.id_, key, secret)
        account.fetch()
        return account

    def request_oauth_access(self):
        """
        Ask for an OAuth token. Return an URL that must be visited for the user
        in order to authenticate the app.
        """
        return self.protocol.request_token()

    def authorize_oauth_access(self, pin):
        """
        Take the *pin* returned by OAuth service and authenticate the token 
        requested with *request_oauth_access*
        """
        self.profile = self.protocol.authorize_token(pin)
        self.__setup(self.profile.username)

    def save(self):
        """
        Save to disk the configuration and credentials for the account. If the 
        account hasn't been authenticated it will raise an 
        :class:`libturpial.exceptions.AccountNotAuthenticated` exception.
        """
        if not self.is_authenticated():
            raise AccountNotAuthenticated

        self.config = AccountConfig(self.id_)
        token = self.get_oauth_token()
        if token:
            self.config.save_oauth_credentials(token.key, token.secret)

    def fetch(self):
        """
        Retrieve the user profile information and return the id of the account 
        on success. This method authenticate the account.
        """
        self.profile = self.protocol.verify_credentials()
        self.lists = self.protocol.get_lists(self.profile.username)

        self.columns = [
            Column(self.id_, ColumnType.TIMELINE),
            Column(self.id_, ColumnType.REPLIES),
            Column(self.id_, ColumnType.DIRECTS),
            Column(self.id_, ColumnType.SENT),
            Column(self.id_, ColumnType.FAVORITES)] + self.lists
        return self.id_

    def fetch_friends(self):
        """
        Retrieve all the friends for the user and return an array of string
        where each element correspond to the user_id of the friend.
        """
        self.friends = self.protocol.get_following(only_id=True)
        return self.friends

    def get_columns(self):
        """
        Return an array of :class:`libturpial.api.models.column.Column` with
        all the available columns for the user
        """
        return self.columns

    def get_list_id(self, list_name):
        if not self.lists:
            return None

        for li in self.lists:
            if li.slug == list_name:
                return li.id_
        return None

    def purge_config(self):
        """
        Delete all config files related to this account
        """
        self.config.dismiss()

    def delete_cache(self):
        """
        Delete all files cached for this account
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
        return self.profile != None and self.id_ != None

    def update_profile(self, fullname=None, url=None, bio=None, location=None):
        """
        Update the *fullname*, *url*, *bio* or *location* of the user profile.
        You may specify one or more arguments. Return an 
        :class:`libturpial.api.models.profile.Profile` object containing the 
        user profile
        """
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
