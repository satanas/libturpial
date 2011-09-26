# -*- coding: utf-8 -*-

""" Module to handle account information """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 13, 2011

from libturpial.config import AccountConfig
from libturpial.api.models.profile import Profile
from libturpial.api.protocols.twitter import twitter
from libturpial.api.protocols.identica import identica
from libturpial.common import ProtocolType, ColumnType

class Account:
    def __init__(self, username, password, account_id, protocol_id):
        self.id_ = account_id
        if protocol_id == ProtocolType.TWITTER:
            self.protocol = twitter.Main(username, self.id_)
        elif protocol_id == ProtocolType.IDENTICA:
            self.protocol = identica.Main(username, self.id_)
        self.profile = Profile()
        self.profile.username = username
        self.profile.password = password
        self.friends = None
        self.columns = []
        self.lists = None
        self.logged_in = False
        self.config = AccountConfig(account_id)
        self.config.initialize()
    
    def auth(self):
        self.profile = self.protocol.auth(self.profile.username, self.profile.password)
        self.lists = self.protocol.get_lists(self.profile.username)
        self.friends = self.protocol.get_friends()
        
        self.columns = [ColumnType.TIMELINE, ColumnType.REPLIES, 
            ColumnType.DIRECTS, ColumnType.SENT, ColumnType.FAVORITES]
        for li in self.lists:
            self.columns.append(li.name)
        self.logged_in = True
        
    def get_friends_list(self):
        return self.friends
        
    def get_columns(self):
        return self.columns
        
    def get_list_id(self, list_name):
        for li in self.lists:
            if li.name == list_name:
                return li.id_
        return None
        
    def update(self, password):
        self.profile.password = password
        
    def set_profile(self, profile):
        self.profile = profile
    
    def remove(self, delete_all):
        if delete_all:
            self.config.dismiss()
        
    def __getattr__(self, name):
        try:
            return getattr(self.protocol, name)
        except:
            try:
                return getattr(self.profile, name)
            except:
                raise AttributeError
