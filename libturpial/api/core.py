# -*- coding: utf-8 -*-

""" Minimalistic and agnostic core for Turpial """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 06, 2011

import ssl
import Queue
import urllib2
import logging
import traceback

from libturpial.common import *
from libturpial.config import AppConfig
from libturpial.api.models.column import Column
from libturpial.api.models.response import Response
from libturpial.api.models.accountmanager import AccountManager
from libturpial.api.services.shorturl.servicelist import URL_SERVICES

# TODO: Implement basic code to identify generic proxies in ui_base

class Core:
    '''Turpial core'''
    def __init__(self, log_level=logging.DEBUG):
        logging.basicConfig(level=log_level)
        
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
        elif _type == ZeroDivisionError:
            response = Response(code=809)
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
        elif _type == ssl.SSLError:
            response = Response(code=810)
        else:
            response = Response(code=999)
        
        self.log.debug(response.errmsg)
        return response
    
    def __apply_filters(self, statuses):
        filtered_statuses = []
        filtered_terms = self.config.load_filter_list()
        if len(filtered_terms) == 0:
            return statuses
        
        for status in statuses:
            for term in filtered_terms:
                if term.startswith('@'):
                    if status.username == term[1:]:
                        continue
                else:
                    if status.text.lower().find(term.lower()) >= 0:
                        continue
                filtered_statuses.append(status)
        return filtered_statuses
    
    ''' Microblogging '''
    def register_account(self, username, protocol_id, password=None, auth=None):
        self.log.debug('Registering account %s' % username)
        acc = self.accman.register(username, protocol_id, password, auth)
        if not acc:
            self.log.debug('Invalid account %s in %s' % (username, protocol_id))
        return acc
    
    def unregister_account(self, account_id, delete_all=False):
        self.log.debug('Unregistering account %s' % account_id)
        return self.accman.unregister(account_id, delete_all)
    
    def load_registered_accounts(self):
        accounts = self.config.get_stored_accounts()
        for acc in accounts:
            self.log.debug('Registering account: %s' % acc)
            self.accman.load(acc)
    
    def register_column(self, column_id):
        count = len(self.reg_columns) + 1
        key = "column%s" % count
        self.config.write('Columns', key, column_id)
        self.load_registered_columns()
        temp = None
        for col in self.reg_columns:
            if col.id_ == column_id:
                temp = col
                break
        return temp
    
    def unregister_column(self, column_id):
        index = 0
        to_store = {}
        for col in self.reg_columns:
            if col.id_ != column_id:
                index += 1
                key = "column%s" % index
                to_store[key] = col.id_
        self.config.write_section('Columns', to_store)
        self.load_registered_columns()
    
    def load_registered_columns(self):
        self.reg_columns = self.config.get_stored_columns()
    
    ''' list_* methods returns arrays of string '''
    def list_accounts(self):
        return self.accman.list()
    
    def list_protocols(self):
        return [ProtocolType.TWITTER, ProtocolType.IDENTICA]
    
    ''' all_* methods returns arrays of objects '''
    def all_accounts(self):
        return self.accman.get_all()
    
    def all_columns(self):
        columns = {}
        for account in self.all_accounts():
            columns[account.id_] = {}
            if account.logged_in != LoginStatus.DONE: continue
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
    
    def change_login_status(self, acc_id, status):
        try:
            account = self.accman.login_status(acc_id, status)
        except Exception, exc:
            return self.__handle_exception(exc)
        
    def login(self, acc_id):
        self.log.debug('Starting login sequence with %s' % acc_id)
        try:
            account = self.accman.get(acc_id, False)
            if account.logged_in == LoginStatus.DONE:
                #add columns
                return Response(code=808)
            else:
                self.accman.login_status(acc_id, LoginStatus.IN_PROGRESS)
                return Response(account.start_login(acc_id))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def authorize_oauth_token(self, acc_id, pin):
        self.log.debug('Authorizating OAuth token for %s' % acc_id)
        try:
            account = self.accman.get(acc_id, False)
            if account.logged_in == LoginStatus.DONE:
                return Response(code=808)
            else:
                return Response(account.authorize_oauth_token(pin))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def auth(self, acc_id):
        try:
            account = self.accman.get(acc_id, False)
            if account.logged_in == LoginStatus.DONE:
                return Response(code=808)
            else:
                self.accman.login_status(acc_id, LoginStatus.DONE)
                return Response(account.auth())
        except Exception, exc:
            self.accman.login_status(acc_id, LoginStatus.NONE)
            return self.__handle_exception(exc)
    
    def get_column_statuses(self, acc_id, col_id, count=STATUSPP):
        try:
            account = self.accman.get(acc_id)
            if col_id == ColumnType.TIMELINE:
                rtn = self.__apply_filters(account.get_timeline(count))
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
            account = self.accman.get(acc_id, False)
            return Response(account.get_public_timeline(count))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def get_followers(self, acc_id, only_id=False):
        try:
            account = self.accman.get(acc_id)
            return Response(account.get_followers(only_id))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def get_following(self, acc_id, only_id=False):
        try:
            account = self.accman.get(acc_id)
            return Response(account.get_following(only_id))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def get_all_friends_list(self):
        friends = []
        try:
            for account in self.accman:
                for profile in account.get_following():
                    if profile.username not in friends:
                        friends.append(profile.username)
            return Response(friends)
        except Exception, exc:
            return self.__handle_exception(exc)
        
    def get_own_profile(self, acc_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.profile)
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def get_user_profile(self, acc_id, user):
        try:
            account = self.accman.get(acc_id)
            profile = account.get_profile(user)
            profile.muted = self.is_muted(profile.username)
            return Response(profile)
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
    
    def broadcast_status(self, acc_array, text):
        responses = []
        for acc_id in acc_array:
            try:
                account = self.accman.get(acc_id)
                resp = Response(account.update_status(text), account_id=acc_id)
                responses.append(resp)
            except Exception, exc:
                resp = self.__handle_exception(exc)
                resp.account_id = acc_id
                responses.append(resp)
        
        return Response(responses)
    
    def destroy_status(self, acc_id, status_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.destroy_status(status_id))
        except Exception, exc:
            return self.__handle_exception(exc)

    def get_single_status(self, acc_id, status_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.get_status(status_id))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def repeat_status(self, acc_id, status_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.repeat(status_id))
        except Exception, exc:
            return self.__handle_exception(exc)

    def unrepeat_status(self, acc_id, status_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.unrepeat(status_id))
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
    
    def follow(self, acc_id, username, by_id=False):
        try:
            account = self.accman.get(acc_id)
            return Response(account.follow(username, by_id))
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
            account = self.accman.get(acc_id, False)
            return Response(account.search(query))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def trends(self, acc_id):
        try:
            account = self.accman.get(acc_id, False)
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
    
    def verify_friendship(self, acc_id, user):
        pass
    
    def is_friend(self, acc_id, user):
        try:
            account = self.accman.get(acc_id)
            return Response(account.is_friend(user))
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def mute(self, user):
        try:
            self.config.append_filter('@%s' % user)
            return Response(user)
        except Exception, exc:
            return self.__handle_exception(exc)
    
    def unmute(self, user):
        try:
            self.config.remove_filter('@%s' % user)
            return Response(user)
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
    
    def is_muted(self, username):
        filtered_terms = self.config.load_filter_list()
        for term in filtered_terms:
            if not term.startswith('@'):
                continue
            
            if username == term[1:]:
                return True
        return False
    
    def get_default_browser(self):
        return self.config.read('Browser', 'cmd')
