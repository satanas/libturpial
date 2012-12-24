# -*- coding: utf-8 -*-

""" Minimalistic and agnostic core for Turpial """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 06, 2011

import os
import ssl
import Queue
import urllib2
import logging
import tempfile
import traceback

from libturpial.common import *
from libturpial.config import AppConfig
from libturpial.common.exceptions import *
from libturpial.common.tools import get_urls
from libturpial.api.models.column import Column
from libturpial.api.models.response import Response
from libturpial.api.models.accountmanager import AccountManager
from libturpial.api.services.shorturl import URL_SERVICES
from libturpial.api.services.uploadpic import PIC_SERVICES
from libturpial.api.services.showmedia import SHOWMEDIA_SERVICES
from libturpial.api.services.showmedia import utils as showmediautils

# TODO: Implement basic code to identify generic proxies in ui_base


class Core:
    """The main core libturpial. This should be the only class you need to
    instanciate to use libturpial.

    Most important params used in Core are:

    * account_id: A composite string formed by the **username** and the **protocol_id**
    * column:id: A composite string formed by **account_id** and the **column-name**

    Examples of account_id:

    >>> my_twitter_account = 'foo-twitter'
    >>> my_identica_account = 'foo-identica'

    Example of column_id:

    >>> twitter_timeline = 'foo-twitter-timeline'
    >>> identica_replies = 'foo-identica-replies'

    Most of Core methods return a
    :class:`libturpial.api.models.reponse.Response` object. If request is
    successful error code will be zero an **items** attribute will hold the
    response for the request. Otherwise error code will be greater than zero
    and errmsg will hold a string with the error message.

    On errors not related to the request methods will return an exception.

    >>> response = c.get_own_profile('foo-twitter')
    >>> if response.code > 0:
    >>>     raise Exception, response.errmsg
    >>> 
    >>> value = response.items

    If the request returns an array, you can iterate over the elements with:

    >>> for v in value:
    >>>     print v
    """
    def __init__(self, log_level=logging.DEBUG):
        logging.basicConfig(level=log_level)

        self.queue = Queue.Queue()
        self.log = logging.getLogger('Core')
        self.log.debug('Started')
        self.config = AppConfig()

        self.accman = AccountManager(self.config)
        self.load_registered_accounts()
        self.load_registered_columns()

    def __print_traceback(self):
        if self.log.getEffectiveLevel() == logging.DEBUG:
            print traceback.print_exc()

    def __handle_exception(self, exc, extra_info=''):
        self.__print_traceback()

        _type = type(exc)
        print "Exception type: %s" % (str(_type))
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
                msg = ''
                errmsg = exc.read()
                self.log.debug("Error HTTP 403 detected: %s" % errmsg)
                if type(errmsg) == str:
                    msg = errmsg
                elif type(errmsg) == dict:
                    if 'error' in errmsg:
                        msg = errmsg['error']
                else:
                    msg = errmsg

                if msg.find("Status is a duplicate.") > 0:
                    response = Response(code=802)
                elif msg.find("is already on your list.") > 0:
                    response = Response(code=802)
                elif msg.find("already requested to follow") > 0:
                    response = Response(code=802)
                elif msg.find("cannot send messages to users who are not following you") > 0:
                    response = Response(code=813)
                elif msg.find("text of your tweet is too long") > 0:
                    response = Response(code=814)
                else:
                    response = Response(code=100)
                    response.errmsg = msg
        elif _type == ValueError:
            response = Response(code=404)
        elif _type == ssl.SSLError:
            response = Response(code=810)
        elif _type == URLShortenError:
            response = Response(code=811)
        elif _type == NoURLException:
            response = Response(code=812)
        elif _type == AlreadyShortURLException:
            response = Response(code=815)
        else:
            response = Response(code=999)

        self.log.debug(response.errmsg)
        return response

    def __apply_filters(self, statuses):
        filtered_statuses = []
        filtered_terms = self.config.load_filters()
        if len(filtered_terms) == 0:
            return statuses

        for status in statuses:
            for term in map(lambda x: x.lower(), filtered_terms):
                if term.startswith('@'):
                    # Filter statuses by user
                    if status.username.lower() == term[1:]:
                        continue
                    # Filter statuses repeated by filtered users
                    elif status.reposted_by:
                        if status.reposted_by.lower().find(term[1:]) >= 0:
                            continue
                else:
                    if status.text.lower().find(term) >= 0:
                        continue
                filtered_statuses.append(status)
        return filtered_statuses

    ''' Microblogging '''
    def register_account(self, username, protocol_id,
                         password=None, auth=None):
        """Register an account for the user *username* and the protocol
        *protocol_id* (see :class:`libturpial.common.ProtocolType` for
        possible values). *password* is neccessary only for Identi.ca accounts,
        Twitter accounts receive None because they use OAuth. **auth** is not
        used anymore (left only for backward compatibility).

        If the account doesn't exist it will create all the needed files to
        store the config.

        Returns a string with the id of the account registered.
        """
        self.log.debug('Registering account %s' % username)
        acc = self.accman.register(username, protocol_id, password, auth)
        if not acc:
            self.log.debug('Invalid account %s in %s' % (username,
                                                         protocol_id))
        return acc

    def unregister_account(self, account_id, delete_all=False):
        """Removes an account form config. If *delete_all* is **True** removes 
        all the config files asociated to that account.
        """
        self.log.debug('Unregistering account %s' % account_id)
        return self.accman.unregister(account_id, delete_all)

    def load_registered_accounts(self):
        """Loads all stored accounts
        """
        accounts = self.config.get_stored_accounts()
        for acc in accounts:
            self.log.debug('Registering account: %s' % acc)
            self.accman.load(acc)

    def register_column(self, column_id):
        """Register the *column_id* column and returns a :class:`Column` object
        """
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
        """Removes the column *column_id* from config.
        """
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
        """Reads the config to load all stored columns
        """
        self.reg_columns = self.config.get_stored_columns()

    def list_accounts(self):
        """Returns an array of registered accounts. For example:

        >>> ['foo-twitter', 'foo-identica']
        """
        return self.accman.list()

    def list_protocols(self):
        """Returns an array of supported protocols. For example:

        >>> ['twitter', 'identica']

        See :class:`libturpial.common.ProtocolType` for more information
        """
        return [ProtocolType.TWITTER, ProtocolType.IDENTICA]

    ''' all_* methods returns arrays of objects '''
    def all_accounts(self):
        """Returns all registered accounts as an array of
        :class:`libturpial.api.models.Account` objects
        """
        return self.accman.get_all()

    def name_as_id(self, acc_id):
        if self.accman.get(acc_id).protocol_id == ProtocolType.TWITTER:
            return self.accman.change_id(acc_id, self.accman.get(acc_id).profile.username)
        else:
            return acc_id

    def all_columns(self):
        """Returns a dictionary with all registered columns per account. Example:

        >>> {'foo-twitter': ['timeline', 'replies', 'direct', 'sent', 'favorites']}
        """
        columns = {}
        for account in self.all_accounts():
            columns[account.id_] = {}
            if account.logged_in != LoginStatus.DONE:
                continue
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
        """Returns an array of :class:`libturpial.api.models.Column` objects
        per column registered
        """
        return self.reg_columns

    def change_login_status(self, acc_id, status):
        try:
            account = self.accman.login_status(acc_id, status)
        except Exception, exc:
            return self.__handle_exception(exc)

    def login(self, acc_id):
        """Starts login sequence for account *acc_id*. Returns a
        :class:`libturpial.api.models.response.Response` object.

        On success, response item will contain a
        :class:`libturpial.api.models.auth_object.AuthObject` object. With this
        object you have to validate if the account requires authorization or not.
        On **True** (needs OAuth authorization), you need to open a browser with
        the URL pointed by **AuthObject**, user must authorize Turpial and then
        write back the PIN returned by the service. After getting the PIN you can
        continue the process with the method
        :meth:`libturpial.api.code.Core.authorize_oauth_token`. If the account
        doesn't require authorization you must continue with the
        :meth:`libturpial.api.core.Core.auth` method.

        On error, response code will be greater than zero.

        >>> acc_id = 'foo-twitter'
        >>> response = c.login(acc_id)
        >>> if response.code > 0:
        >>>     raise Exception
        >>> 
        >>> auth_obj = response.items
        >>> # Validates if account needs authorization
        >>> if auth_obj.must_auth():
        >>>     print "Visit %s, authorize Turpial and write back the pin" % auth_obj.url
        >>>     pin = raw_input('Pin: ')
        >>>     c.core.authorize_oauth_token(acc_id, pin)
        >>> 
        >>> # Continue with the authentication process
        """
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
        """Authorize an OAuth token for the account *account_id* with the given
        *pin*. Returns a
        :class:`libturpial.api.models.response.Response` object. You need to
        validate response code because on success response items will be
        **None**
        """
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
        """Second step on login sequence (after authorization). This method will
        authenticate account *acc_id* against service (Twitter, Identica, etc)
        and returns a :class:`libturpial.api.models.response.Response` object.
        On success response items will hold the id of the authenticated
        account.
        """
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

    def get_column_statuses(self, acc_id, col_id,
                            count=STATUSPP, since_id=None):
        """Fetch the statuses for the account *acc_id* and the column *col_id*.
        *count* let you specify how many statuses do you want to fetch, values
        range goes from 0-200. If *since_id* is not **None** libturpial will
        only fetch statuses newer than that.
        """
        try:
            account = self.accman.get(acc_id)
            if col_id.find(ColumnType.SEARCH) == 0:
                criteria = col_id[len(ColumnType.SEARCH) + 1:]
                rtn = account.search(criteria, count)
            elif col_id == ColumnType.TIMELINE:
                rtn = self.__apply_filters(account.get_timeline(count, since_id))
            elif col_id == ColumnType.REPLIES:
                rtn = account.get_replies(count, since_id)
            elif col_id == ColumnType.DIRECTS:
                rtn = account.get_directs(count, since_id)
            elif col_id == ColumnType.SENT:
                rtn = account.get_sent(count, since_id)
            elif col_id == ColumnType.FAVORITES:
                rtn = account.get_favorites(count)
            elif col_id == ColumnType.PUBLIC:
                rtn = account.get_public_timeline(count, since_id)
            else:
                list_id = account.get_list_id(col_id)
                if list_id is None:
                    raise IndexError
                rtn = account.get_list_statuses(list_id, count, since_id)
                print len(rtn), rtn
            return Response(rtn)
        except Exception, exc:
            return self.__handle_exception(exc)

    def get_public_timeline(self, acc_id, count=STATUSPP, since_id=None):
        """Fetch the public timeline for the service associated to the
        account *acc_id*. *count* and *since_id* work in the same way
        that in :meth:`libturpial.api.core.Core.get_column_statuses`
        """
        try:
            account = self.accman.get(acc_id, False)
            return Response(account.get_public_timeline(count, since_id))
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
            for account in self.accman.get_all():
                print account
                for profile in account.get_following():
                    if profile not in friends:
                        friends.append(profile)
            self.config.save_friends([f.username for f in friends])
            return Response(friends)
        except Exception, exc:
            return self.__handle_exception(exc)

    def load_all_friends_list(self):
        return self.config.load_friends()

    def get_own_profile(self, acc_id):
        try:
            account = self.accman.get(acc_id)
            return Response(account.profile)
        except Exception, exc:
            return self.__handle_exception(exc)

    def get_user_profile(self, acc_id, user):
        try:
            account = self.accman.get(str(acc_id))
            profile = account.get_profile(str(user))
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
            account = self.accman.get(str(acc_id))
            return Response(account.update_status(str(text), str(in_reply_id)))
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
            account = self.accman.get(str(acc_id))
            return Response(account.destroy_status(str(status_id)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def get_single_status(self, acc_id, status_id):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.get_status(str(status_id)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def repeat_status(self, acc_id, status_id):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.repeat(str(status_id)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def unrepeat_status(self, acc_id, status_id):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.unrepeat(str(status_id)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def update_profile(self, acc_id, args):
        try:
            account = self.accman.get(str(acc_id))
            new_profile = account.update_profile(args)
            account.set_profile(new_profile)
            return Response(new_profile)
        except Exception, exc:
            return self.__handle_exception(exc)

    def follow(self, acc_id, username, by_id=False):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.follow(str(username), str(by_id)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def unfollow(self, acc_id, username):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.unfollow(str(username)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def send_direct(self, acc_id, username, message):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.send_direct(str(username), str(message)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def destroy_direct(self, acc_id, status_id):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.destroy_direct(str(status_id)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def mark_favorite(self, acc_id, status_id):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.mark_favorite(status_id))
        except Exception, exc:
            return self.__handle_exception(exc)

    def unmark_favorite(self, acc_id, status_id):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.unmark_favorite(str(status_id)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def search(self, acc_id, query):
        try:
            account = self.accman.get(str(acc_id), False)
            return Response(account.search(str(query)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def trends(self, acc_id):
        try:
            account = self.accman.get(str(acc_id), False)
            return Response(account.trends())
        except Exception, exc:
            return self.__handle_exception(exc)

    def block(self, acc_id, user):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.block(str(user)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def unblock(self, acc_id, user):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.unblock(str(user)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def report_spam(self, acc_id, user):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.report_spam(user))
        except Exception, exc:
            return self.__handle_exception(exc)

    def verify_friendship(self, acc_id, user):
        pass

    def is_friend(self, acc_id, user):
        try:
            account = self.accman.get(str(acc_id))
            return Response(account.is_friend(str(user)))
        except Exception, exc:
            return self.__handle_exception(exc)

    def mute(self, user):
        try:
            self.config.append_filter('@%s' % str(user))
            return Response(str(user))
        except Exception, exc:
            return self.__handle_exception(exc)

    def unmute(self, user):
        try:
            self.config.remove_filter('@%s' % str(user))
            return Response(user)
        except Exception, exc:
            return self.__handle_exception(exc)

    def get_profile_image(self, acc_id, user):
        # Returns the path of profile image in original size
        try:
            account = self.accman.get(str(acc_id))
            basename = "%s-%s-profile-image" % (acc_id, user)
            img_path = os.path.join(account.config.imgdir, basename)
            if os.path.isfile(img_path):
                self.log.debug('Getting profile image for %s from cache' % user)
            else:
                fd = open(img_path, 'w')
                fd.write(account.get_profile_image(str(user)))
                fd.close()
            return Response(img_path)
        except Exception, exc:
            return self.__handle_exception(exc)

    def get_status_avatar(self, status):
        # Returns the path of profile image for the user who post the status
        # in avatar size (48x48)
        try:
            account = self.accman.get(status.account_id)
            basename = "%s-%s-avatar-%s" % (status.account_id, status.username, os.path.basename(status.avatar))
            img_path = os.path.join(account.config.imgdir, basename)
            if not os.path.isfile(img_path):
                handle = urllib2.urlopen(status.avatar)
                fp = open(img_path, 'w')
                fp.write(handle.read())
                fp.close()
            return Response(img_path)
        except Exception, exc:
            return self.__handle_exception(exc)

    ''' Services '''
    def list_short_url_services(self):
        return URL_SERVICES.keys()

    def short_url(self, url):
        service = self.config.read('Services', 'shorten-url')
        try:
            # Validate already shorten URLs
            if os.path.split(url)[0].find(service) >= 0:
                raise AlreadyShortURLException
            urlshorter = URL_SERVICES[service]
            resp = urlshorter.do_service(str(url))
            return Response(resp.response)
        except Exception, exc:
            return self.__handle_exception(exc)

    def autoshort_url(self, message):
        message = str(message)
        try:
            all_urls = get_urls(message)
            if len(all_urls) == 0:
                raise NoURLException

            code = 0
            for url in all_urls:
                response = self.short_url(url)
                if response.code == 0:
                    message = message.replace(url, response.items)
                elif response.code > 0 and code == 0:
                    code = response.code
            response = Response(message)
            response.code = code
            return response
        except Exception, exc:
            response = self.__handle_exception(exc)
            response.items = message
            return response

    def get_media_content(self, url, acc_id):
        service = showmediautils.get_service_from_url(str(url))
        try:
            return service.do_service(str(url))
        except Exception, exc:
            return self.__handle_exception(exc)

    def list_upload_pic_services(self):
        return PIC_SERVICES.keys()

    def upload_pic(self, acc_id, filepath, message):
        service = self.config.read('Services', 'upload-pic')
        try:
            account = self.accman.get(str(acc_id))
            uploader = PIC_SERVICES[service].do_service(account, filepath, message)
            return Response(uploader.response)
        except Exception, exc:
            return self.__handle_exception(exc)


    ''' Configuration '''
    def has_stored_passwd(self, acc_id):
        account = self.accman.get(str(acc_id))
        if account.profile.password is None:
            return False
        if account.profile.password == '':
            return False
        return True

    def is_account_logged_in(self, acc_id):
        account = self.accman.get(str(acc_id))
        return account.logged_in

    def is_muted(self, username):
        filtered_terms = self.config.load_filters()
        for term in filtered_terms:
            if not term.startswith('@'):
                continue

            if username == term[1:]:
                return True
        return False

    def get_default_browser(self):
        return self.config.read('Browser', 'cmd')

    def show_notifications_in_login(self):
        temp = self.config.read('Notifications', 'login')
        if temp == 'on':
            return True
        return False

    def show_notifications_in_updates(self):
        temp = self.config.read('Notifications', 'updates')
        if temp == 'on':
            return True
        return False

    def play_sounds_in_login(self):
        temp = self.config.read('Sounds', 'login')
        if temp == 'on':
            return True
        return False

    def play_sounds_in_updates(self):
        temp = self.config.read('Sounds', 'updates')
        if temp == 'on':
            return True
        return False

    def get_max_statuses_per_column(self):
        return int(self.config.read('General', 'statuses'))

    def get_update_interval(self):
        return int(self.config.read('General', 'update-interval'))

    def minimize_on_close(self):
        minimize = self.config.read('General', 'minimize-on-close')
        return True if minimize == 'on' else False

    def get_config(self):
        return self.config.read_all()

    def read_config_value(self, section, option):
        return self.config.read(section, option)

    def write_config_value(self, section, option, value):
        self.config.write(section, option, value)

    def save_all_config(self, new_config):
        self.config.save(new_config)

    def list_filters(self):
        return self.config.load_filters()

    def save_filters(self, lst):
        self.config.save_filters(lst)

    def delete_current_config(self):
        self.config.delete_current_config()

    def delete_cache(self):
        for account in self.all_accounts():
            account.delete_cache()

    def get_cache_size(self):
        total_size = 0
        for account in self.all_accounts():
            total_size += account.get_cache_size()
        return total_size
