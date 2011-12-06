# -*- coding: utf-8 -*-

""" Minimalistic and agnostic core for Turpial """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 06, 2011

import Queue
import urllib2
import logging
import traceback

from libturpial.api.models.column import Column
from libturpial.api.models.response import Response
from libturpial.config import AppConfig, AccountConfig
from libturpial.api.models.accountmanager import AccountManager
from libturpial.api.services.shorturl.servicelist import URL_SERVICES
from libturpial.common import ProtocolType, ColumnType, STATUSPP, ERROR_CODES

# TODO: Implement basic code to identify generic proxies in ui_base

class Core:
    '''Turpial core'''
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        
        self.queue = Queue.Queue()
        self.log = logging.getLogger('Core')
        self.log.debug('Started')
        self.accman = AccountManager()
        self.config = AppConfig()
        
        self.load_registered_accounts()
        self.load_registered_columns()
        
    def __print_traceback(self):
        if self.log.getEffectiveLevel() == logging.DEBUG:
            print traceback.print_exc()
    
    def __handle_exception(self, exc, extra_info=''):
        self.__print_traceback()
        
        _type = type(exc)
        response = None
        if _type == urllib2.URLError:
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
                self.log.debug("Error HTTP 400 detected: %s" % exc)
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
        elif _type == ValueError:
            response = Response(code=404)
        else:
            response = Response(code=999)
        
        self.log.debug(response.errmsg)
        return response
    
    ''' Microblogging '''
    def register_account(self, username, protocol_id, password=None, remember=False, auth=None):
        self.log.debug('Registering account %s' % username)
        acc = self.accman.register(username, protocol_id, password, remember, auth)
        if not acc:
            self.log.debug('Invalid account %s in %s' % (username, protocol_id))
        return acc
    
    def unregister_account(self, account_id, delete_all=False):
        self.log.debug('Unregistering account %s' % account_id)
        return self.accman.unregister(account_id, delete_all)
        
    def load_registered_accounts(self):
        accounts = self.config.get_stored_accounts()
        for acc in accounts:
            cfg = AccountConfig(acc)
            auth = cfg.read_section('OAuth')
            username = cfg.read('Login', 'username')
            protocol = cfg.read('Login', 'protocol')
            password = cfg.revert(cfg.read('Login', 'password'), username)
            rem = False
            if password:
                rem = True
            self.register_account(username, protocol, password, rem, auth)
    
    def register_column(self, column_id):
        count = len(self.reg_columns) + 1
        key = "column%s" % count
        self.config.write('Columns', key, column_id)
        self.load_registered_columns()
        
    def load_registered_columns(self):
        self.reg_columns = self.config.get_stored_columns()
    
    ''' list_* methods returns arrays of string '''
    def list_accounts(self):
        return self.accman.list()
    
    def list_protocols(self):
        return [ProtocolType.TWITTER, ProtocolType.IDENTICA]
    '''
    def list_columns(self):
        columns = {}
        for account in self.all_accounts():
            if not account.logged_in: continue
            columns[account.id_] = account.get_columns()
        return columns
        
    def list_columns_per_account(self, acc_id):
        account = self.accman.get(acc_id)
        return account.get_columns()
    
    def list_stored_columns(self):
        return self.config.get_stored_columns()
    
    def update_stored_columns(self, columns):
        
    '''
    
    ''' all_* methods returns arrays of objects '''
    def all_accounts(self):
        return self.accman.get_all()
    
    def all_columns(self):
        columns = {}
        for account in self.all_accounts():
            columns[account.id_] = {}
            if not account.logged_in: continue
            for col in account.get_columns():
                id_ = ""
                for reg in self.reg_columns:
                    if account.id_ == reg.account_id and reg.column_name == col:
                        id_ = reg.id_
                        break
                item = Column(id_, account.id_, account.protocol_id, col)
                columns[account.id_][col] = item
        return columns
    
    def all_registered_columns(self):
        return self.reg_columns
    
    def login(self, acc_id):
        self.log.debug('Starting login sequence with %s' % acc_id)
        try:
            account = self.accman.get(acc_id)
            if account.logged_in:
                #add columns
                return Response(code=808)
            else:
                return Response(account.start_login(acc_id))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def authorize_oauth_token(self, acc_id, pin):
        self.log.debug('Authorizating OAuth token for %s' % acc_id)
        try:
            account = self.accman.get(acc_id)
            if account.logged_in:
                return Response(code=808)
            else:
                return Response(account.authorize_oauth_token(pin))
        except Exception, exc:
            return self.__handle_exception(exc)
            
    def auth(self, acc_id):
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
    
    def get_public_timeline(self, acc_id, count=STATUSPP):
        try:
            account = self.accman.get(acc_id)
            return Response(account.get_public_timeline(count))
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
    
    def get_conversation(self, acc_id, status_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.get_conversation(status_id))
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
    
    def is_friend(self, acc_id, user):
        try:
            account = self.accman.get(acc_id)
            return Response(account.is_friend(user))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    ''' Services '''
    def short_url(self, url, service):
        urlshorter = URL_SERVICES[service].do_service(url)
        return urlshorter.response
        
    ''' Configuration '''
    def has_stored_passwd(self, acc_id):
        account = self.accman.get(acc_id)
        if account.profile.password is None:
            return False
        if account.profile.password == '':
            return False
        return True
        
    def is_account_logged_in(self, acc_id):
        account = self.accman.get(acc_id)
        return account.logged_in
