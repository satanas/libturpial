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
from libturpial.api.services.shorturl.servicelist import URL_SERVICES

# TODO: Implement basic code to identify generic proxies in ui_base

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
    
    def __handle_exception(self, exc, extra_info=''):
        self.__print_traceback()
        
        _type = type(exc)
        response = None
        if _type == urllib2.URLError:
            response = Response(code=801)
        elif _type == urllib2.HTTPError:
            response = Response(code=801)
        elif _type == IndexError:
            return Response(code=808)
        elif _type == KeyError:
            response = Response(code=807)
        elif _type == NotImplementedError:
            response = Response(code=900)
        elif _type == urllib2.HTTPError:
            if exc.code in ERROR_CODES:
                response = Response(code=exc.code)
            elif (exc.code == 400):
                self.log.debug("Error HTTP 400 detected: %s" % msg)
                response = Response(code=100)
                response.errmsg = "Sorry, server is limiting your API calls"
            elif (exc.code == 403):
                msg = exc.read()
                self.log.debug("Error HTTP 403 detected: %s" % msg)
                if msg.find("Status is a duplicate.") > 0:
                    response = Response(code=802)
                elif msg.find("is already on your list.") > 0:
                    response = Response(code=802)
                elif msg.find("already requested to follow") > 0:
                    response = Response(code=802)
                else:
                    response = Response(code=100)
                    response.errmsg = msg
        elif _type == Exception:
            response = Response(code=999)
        
        self.log.debug(response.errmsg)
        return response
    
    ''' Microblogging '''
    def register_account(self, username, password, protocol_id):
        self.log.debug('Registering account %s' % username)
        return self.accman.register(username, password, protocol_id)
    
    def unregister_account(self, account_id):
        self.log.debug('Unregistering account %s' % account_id)
        return self.accman.unregister(account_id)
    
    def list_accounts(self):
        return self.accman.list()
    
    def list_protocols(self):
        return [ProtocolType.TWITTER, ProtocolType.IDENTICA]
    
    def list_columns(self, acc_id):
        account = self.accman.get(acc_id)
        return account.get_columns()
    
    def login(self, acc_id):
        self.log.debug('Authenticating with %s' % acc_id)
        try:
            account = self.accman.get(acc_id)
            if account.logged_in:
                return Response(code=808)
            else:
                return Response(account.auth())
        except Exception, exc:
            return self.__handle_exception(exc)
    
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
            else:
                list_id = account.get_list_id(col_id)
                if list_id is None:
                    raise IndexError
                rtn = account.get_list_statuses(list_id, count)
            return Response(rtn)
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def get_friends(self, acc_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.get_friends_list())
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def get_own_profile(self, acc_id):
        try:
            account = self.accman.get(acc_id)
            return Response([account.profile])
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def get_user_profile(self, acc_id, user):
        try:
            account = self.accman.get(acc_id)
            return Response([account.get_profile(user)])
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def update_status(self, acc_id, text, in_reply_id=None):
        try:
            account = self.accman.get(acc_id)
            return Response(account.update_status(text, in_reply_id))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def destroy_status(self, acc_id, status_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.destroy_status(status_id))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def repeat_status(self, acc_id, status_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.repeat(status_id))
        except Exception, exc:
            return self.__handle_exception(exc)
            
    def update_profile(self, acc_id, args):
        try:
            account = self.accman.get(acc_id)
            new_profile = account.update_profile(args)
            account.set_profile(new_profile)
            return Response(new_profile)
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def follow(self, acc_id, username):
        try:
            account = self.accman.get(acc_id)
            return Response(account.follow(username))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def unfollow(self, acc_id, username):
        try:
            account = self.accman.get(acc_id)
            return Response(account.unfollow(username))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def send_direct(self, acc_id, username, message):
        try:
            account = self.accman.get(acc_id)
            return Response(account.send_direct(username, message))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def destroy_direct(self, acc_id, status_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.destroy_direct(status_id))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def mark_favorite(self, acc_id, status_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.mark_favorite(status_id))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def unmark_favorite(self, acc_id, status_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.unmark_favorite(status_id))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def search(self, acc_id, query):
        try:
            account = self.accman.get(acc_id)
            return Response(account.search(query))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def trends(self, acc_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.trends())
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def block(self, acc_id, user):
        try:
            account = self.accman.get(acc_id)
            return Response(account.block(user))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def unblock(self, acc_id, user):
        try:
            account = self.accman.get(acc_id)
            return Response(account.unblock(user))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def report_spam(self, acc_id, user):
        try:
            account = self.accman.get(acc_id)
            return Response(account.report_spam(user))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    ''' Services '''
    def short_url(self, url, service):
        urlshorter = URL_SERVICES[service].do_service(url)
        return urlshorter.response
        
