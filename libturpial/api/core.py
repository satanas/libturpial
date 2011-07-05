# -*- coding: utf-8 -*-

'''Minimalistic and agnostic core for Turpial'''
#
# Author: Wil Alvarez (aka Satanas)
# Mar 06, 2011

import os
import Queue
import urllib2
import logging
import traceback

from libturpial.common import ProtocolType, ColumnType, STATUSPP
from libturpial.api.models.response import Response
from libturpial.api.models.accountmanager import AccountManager

#TODO: Implement basic code to identify generic proxies in ui_base

class Core:
    '''Turpial core'''
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        
        self.queue = Queue.Queue()
        self.log = logging.getLogger('Core')
        self.log.debug('Started')
        self.accman = AccountManager()
        
    def __print_traceback(self):
        if self.log.getEffectiveLevel() == logging.DEBUG:
            print traceback.print_exc()
            
    def register_account(self, username, password, protocol_id):
        self.log.debug('Registering account %s' % username)
        return self.accman.register(username, password, protocol_id)
        
    def list_accounts(self):
        return self.accman.list()
        
    def list_protocols(self):
        return [ProtocolType.TWITTER, ProtocolType.IDENTICA]
        
    def login(self, acc_id):
        self.log.debug('Authenticating with %s' % acc_id)
        try:
            account = self.accman.get(acc_id)
            return Response(account.auth())
        except Exception, exc:
            self.__print_traceback()
            self.log.debug('Authentication Error')
            return Response(code=401)
        
    def get_column_statuses(self, acc_id, col_id, count=STATUSPP):
        try:
            account = self.accman.get(acc_id)
            if col_id == ColumnType.TIMELINE:
                rtn = account.get_timeline(count)
            elif col_id == ColumnType.REPLIES:
                rtn = account.get_replies(count)
            elif col_id == ColumnType.DIRECTS:
                rtn = account.get_directs(count)
            elif col_id == ColumnType.SENT:
                rtn = account.get_sent(count)
            elif col_id == ColumnType.FAVORITES:
                rtn = account.get_favorites(count)
            return Response(rtn)
        except KeyError:
            return Response(code=410)
        except urllib2.HTTPError, exc:
            if exc.code == 401:
                return Response(code=401)
    
    def get_friends(self, acc_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.get_friends())
        except Exception:
            self.log.debug('Error getting friends list')
            return Response(code=411)
            
    def get_own_profile(self, acc_id):
        try:
            account = self.accman.get(acc_id)
            return Response([account.profile])
        except KeyError, exc:
            self.log.debug('Error getting user profile')
            return Response(code=409)
    
    def get_user_profile(self, acc_id, user):
        try:
            account = self.accman.get(acc_id)
            return Response([account.get_profile(user)])
        except Exception:
            self.log.debug('Error getting user profile')
            return Response(code=409)
            
    def update_status(self, acc_id, text, in_reply_id=None):
        try:
            account = self.accman.get(acc_id)
            return Response(account.update_status(text, in_reply_id))
        except Exception, exc:
            self.__print_traceback()
            self.log.debug('Error updating status')
            return Response(code=999)
            
    def unfollow(self, acc_id, username):
        try:
            account = self.accman.get(acc_id)
            return Response(account.unfollow(username))
        except Exception, exc:
            self.__print_traceback()
            self.log.debug('Error unfolowing user')
            return Response(code=999)
    
        
