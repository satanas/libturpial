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
    def __init__(self, username, account_id, protocol_id, password, remember, auth):
        self.id_ = account_id # username-protocol_id
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
        self.logged_in = LoginStatus.NONE
        self.remembered = remember
        self.config = AccountConfig(account_id, password, remember)
        
        if self.config.read('Login', 'active') == 'on':
            self.active = True
        else:
            self.active = False
    
    def auth(self):
        self.profile = self.protocol.auth(self.profile.username, self.profile.password)
        self.lists = self.protocol.get_lists(self.profile.username)
        
        self.columns = [ColumnType.TIMELINE, ColumnType.REPLIES, 
            ColumnType.DIRECTS, ColumnType.SENT, ColumnType.FAVORITES]
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
    
    def is_remembered(self):
        return self.remembered
    
    def is_active(self):
        return self.active
        
    def update(self, pw, remember):
        self.profile.password = pw
        self.remembered = remember
        if remember:
            self.config.remember(pw, self.profile.username)
        else:
            self.config.forget()
        
    def set_profile(self, profile):
        self.profile = profile
    
    def remove(self, delete_all):
        if delete_all:
            self.config.dismiss()
    
    def authorize_oauth_token(self, pin):
        token = self.authorize_token(pin)
        self.config.write('OAuth', 'key', token.key)
        self.config.write('OAuth', 'secret', token.secret)
        self.config.write('OAuth', 'verifier', token.verifier)
        
    def activate(self, value):
        if value:
            self.config.write('Login', 'active', 'on')
        else:
            self.config.write('Login', 'active', 'off')
        
    def __getattr__(self, name):
        try:
            return getattr(self.protocol, name)
        except:
            try:
                return getattr(self.profile, name)
            except:
                raise AttributeError
