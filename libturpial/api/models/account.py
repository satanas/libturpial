# -*- coding: utf-8 -*-

""" Module to handle account information """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 13, 2011

from libturpial.common import *
from libturpial.config import AccountConfig
from libturpial.api.models.profile import Profile
from libturpial.api.protocols.twitter import twitter
from libturpial.api.protocols.identica import identica


class Account:
    def __init__(self, username, account_id, protocol_id,
                 password, auth, config=None):
        self.id_ = account_id  # username-protocol_id
        self.username = username
        self.protocol_id = protocol_id

        if protocol_id == ProtocolType.TWITTER:
            self.protocol = twitter.Main(username, self.id_, auth)
        elif protocol_id == ProtocolType.IDENTICA:
            self.protocol = identica.Main(username, self.id_, auth)

        self.profile = Profile()
        self.profile.username = username
        self.profile.password = password
        self.friends = None
        self.columns = []
        self.lists = None
        #self.token = None
        self.logged_in = LoginStatus.NONE
        if config:
            self.config = config
        else:
            self.config = AccountConfig(account_id, password)

    def auth(self):
        self.profile = self.protocol.auth(self.profile.username,
                                          self.profile.password)
        self.lists = self.protocol.get_lists(self.profile.username)

        self.columns = [ColumnType.TIMELINE, ColumnType.REPLIES,
                        ColumnType.DIRECTS, ColumnType.SENT,
                        ColumnType.FAVORITES]
        for li in self.lists:
            self.columns.append(li.name)
        return self.id_

    def get_friends(self):
        self.friends = self.protocol.get_friends()
        return self.friends

    def get_columns(self):
        return self.columns

    def get_list_id(self, list_name):
        for li in self.lists:
            if li.name == list_name:
                return li.id_
        return None

    def update(self, passwd):
        self.profile.password = passwd

    def set_profile(self, profile):
        self.profile = profile

    def remove(self, delete_all):
        if delete_all:
            self.config.dismiss()

    def authorize_oauth_token(self, pin):
        token = self.authorize_token(pin)
        self.store_token(token)

    def store_token(self, token):
        self.config.write('OAuth', 'key', token.key)
        self.config.write('OAuth', 'secret', token.secret)
        self.config.write('OAuth', 'verifier', token.verifier)

    def delete_cache(self):
        self.config.delete_cache()

    def get_cache_size(self):
        return self.config.calculate_cache_size()

    def __getattr__(self, name):
        try:
            return getattr(self.protocol, name)
        except:
            try:
                return getattr(self.profile, name)
            except:
                raise AttributeError
