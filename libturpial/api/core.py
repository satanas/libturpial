# -*- coding: utf-8 -*-

""" Minimalistic and agnostic core for Turpial """

import os
import urllib2
import requests

from libturpial.common import *
from libturpial.exceptions import *
from libturpial.config import AppConfig
from libturpial.common.tools import get_urls
from libturpial.api.models.proxy import Proxy
from libturpial.api.models.column import Column
from libturpial.api.models.account import Account
from libturpial.lib.interfaces.protocol import Protocol
from libturpial.lib.services.url import URL_SERVICES
from libturpial.lib.services.media.upload import UPLOAD_MEDIA_SERVICES
from libturpial.lib.services.media.preview import PREVIEW_MEDIA_SERVICES
from libturpial.api.managers.accountmanager import AccountManager
from libturpial.api.managers.columnmanager import ColumnManager


class Core:
    """
    This is the main object in libturpial. This should be the only class you need to
    instantiate to use libturpial. Most important arguments used in Core are
    *account_id* and *column_id*.

    * account_id: Is a composite string formed by the **username** and the
      **protocol_id** that identify every single account.
    * column_id: Is composite string formed by **account_id** and the
      **column_name** that identify one column of one account.

    Examples of account_id:

    >>> my_twitter_account = 'foo-twitter'
    >>> my_identica_account = 'foo-identica'

    Example of column_id:

    >>> twitter_timeline = 'foo-twitter-timeline'
    >>> identica_replies = 'foo-identica-replies'

    When you instantiate Core it will load all registered accounts
    automatically, so you don't need to worry about it. If you already registered the
    accounts before, they will be available after you create the core object.

    All the Core methods will return an object defined in
    :class:`libturpial.api.models` or a valid python object if request is
    successful, otherwise they will raise an exception.

    If the request returns an array, you can iterate over the elements with:

    >>> for object in response:
    >>>     print object

    In all the following functions the following apply:
        *account_id* must be a string ("username-service")
        *column_id* must be a string ("columnname-username-service")
    """

    def __init__(self, load_accounts=True):
        self.config = AppConfig()
        self.accman = AccountManager(self.config, load_accounts)
        self.column_manager = ColumnManager(self.config)

    def __get_upload_media_object(self, service):
        return UPLOAD_MEDIA_SERVICES[service]

    def __get_short_url_object(self, service):
        return URL_SERVICES[service]

    def filter_statuses(self, statuses):
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
                    elif status.repeated_by:
                        if status.repeated_by.lower().find(term[1:]) >= 0:
                            continue
                else:
                    if status.text.lower().find(term) >= 0:
                        continue
                filtered_statuses.append(status)
        return filtered_statuses

    def fetch_image(self, url):
        """
        Retrieve an image by it *URL*. Return the binary data of the image
        """
        response = requests.get(url)
        return response.content

    ###########################################################################
    # Multi-account and multi-column API
    ###########################################################################

    def list_accounts(self):
        """
        Return an array with the ids of all registered accounts. For example:

        >>> ['foo-twitter', 'foo-identica']
        """
        return self.accman.list()

    def register_account(self, account):
        # TODO: Add documention/reference for account validation
        """
        Register *account* into config files. *account* must be a
        valid and authenticated :class:`libturpial.api.models.account.Account`
        object.

        When instantiating Core() all accounts get automatically registered.

        Return a string with the id of the account registered.
        """
        return self.accman.register(account)

    def unregister_account(self, account_id, delete_all=False):
        """
        Removes the account identified by *account_id* from memory. If
        *delete_all* is **True** it deletes all the files asociated to
        that account from disk otherwise the account will be available
        the next time you load Core.

        Return a string with the id of the account unregistered.
        """
        return self.accman.unregister(account_id, delete_all)

    def all_columns(self):
        """
        Return a dictionary with all columns per account. Example:

        >>> {'foo-twitter': [libturpial.api.models.Column foo-twitter-timeline,
            libturpial.api.models.Column foo-twitter-replies,
            libturpial.api.models.Column foo-twitter-direct,
            libturpial.api.models.Column foo-twitter-sent,
            libturpial.api.models.Column foo-twitter-favorites]}
        """
        columns = {}
        for account in self.registered_accounts():
            columns[account.id_] = []
            for column in account.get_columns():
                columns[account.id_].append(column)
        return columns


    def register_column(self, column_id):
        """
        Register a column identified by *column_id* column and return a string
        with the id of the column registered on success.
        """
        return self.column_manager.register(column_id)

    def unregister_column(self, column_id):
        """
        Removes the column identified by *column_id* from config and return a
        string with the id if the column unregistered on success.
        """
        return self.column_manager.unregister(column_id)

    def list_protocols(self):
        """
        Return an array with the ids of supported protocols. For example:

        >>> ['twitter', 'identica']
        """
        return Protocol.availables()


    def available_columns(self):
        """
        Return a dictionary with all available (non-registered-yet)
        columns per account. Example:

        >>> {'foo-twitter': [libturpial.api.models.Column foo-twitter-direct,
            libturpial.api.models.Column foo-twitter-replies,
            libturpial.api.models.Column foo-twitter-sent]}
        """
        columns = {}
        for account in self.registered_accounts():
            columns[account.id_] = []
            for column in account.get_columns():
                if not self.column_manager.is_registered(column.id_):
                    columns[account.id_].append(column)
        return columns

    def registered_columns(self):
        """
        Return a *dict* with :class:`libturpial.api.models.column.Column` objects
        per column registered. This method DO NOT return columns in the order they
        have been registered. For ordered columns check
        :meth:`registered_columns_by_order()`
        """
        return self.column_manager.columns()

    def registered_columns_by_order(self):
        """
        Return a *list* with :class:`libturpial.api.models.column.Column` objects
        per each column in the same order they have been registered.
        """
        return self.column_manager.columns_by_order()

    def registered_accounts(self):
        """
        Return a *dict* with all registered accounts as an array of
        :class:`libturpial.api.models.account.Account` objects registered
        """
        return self.accman.accounts()

    def get_single_column(self, column_id):
        """
        Return the :class:`libturpial.api.models.column.Column` object identified
        with *column_id*
        """
        return self.column_manager.get(column_id)

    def get_single_account(self, account_id):
        """
        Return the :class:`libturpial.api.models.account.Account` object identified
        with *account_id*
        """
        return self.accman.get(account_id)


    ###########################################################################
    # Microblogging API
    ###########################################################################

    def get_column_statuses(self, account_id, column_id,
                            count=NUM_STATUSES, since_id=None):
        """
        Fetch the statuses for the account *account_id* and the column *column_id*.
        *count* let you specify how many statuses do you want to fetch, values
        range goes from 0-200. If *since_id* is not **None** libturpial will
        only fetch statuses newer than that.

        """
        if column_id.find(ColumnType.SEARCH) == 0:
            criteria = column_id[len(ColumnType.SEARCH) + 1:]
            return self.search(account_id, criteria, count, since_id)

        account = self.accman.get(account_id)
        if column_id == ColumnType.TIMELINE:
            rtn = account.get_timeline(count, since_id)
        elif column_id == ColumnType.REPLIES:
            rtn = account.get_replies(count, since_id)
        elif column_id == ColumnType.DIRECTS:
            rtn = account.get_directs(count, since_id)
        elif column_id == ColumnType.SENT:
            rtn = account.get_sent(count, since_id)
        elif column_id == ColumnType.FAVORITES:
            rtn = account.get_favorites(count)
        elif column_id == ColumnType.PUBLIC:
            rtn = account.get_public_timeline(count, since_id)
        else:
            list_id = account.get_list_id(column_id)
            if list_id is None:
                raise UserListNotFound
            rtn = account.get_list_statuses(list_id, count, since_id)
        return rtn

    def get_public_timeline(self, account_id, count=NUM_STATUSES, since_id=None):
        # TODO: Remove this function and replace with streamming api
        """
        Fetch the public timeline for the service associated to the
        account *account_id*. *count* and *since_id* work in the same way
        that in :meth:`libturpial.api.core.Core.get_column_statuses`
        """
        account = self.accman.get(account_id)
        return account.get_public_timeline(count, since_id)

    def get_followers(self, account_id, only_id=False):
        """
        Return a :class:`libturpial.api.models.profile.Profile` list with
        all the followers of the account *account_id*
        """
        account = self.accman.get(account_id)
        return account.get_followers(only_id)

    def get_following(self, account_id, only_id=False):
        """
        Return a :class:`libturpial.api.models.profile.Profile` list of
        all the accounts that *account_id* follows
        """
        account = self.accman.get(account_id)
        return account.get_following(only_id)

    def get_all_friends_list(self):
        """
        Return a list with all the username friends of all the registered
        accounts.
        """
        friends = []
        for account in self.accman.accounts():
            for profile in account.get_following():
                if profile.username not in friends:
                    friends.append(profile.username)
        self.config.save_friends(friends)
        return friends

    def load_all_friends_list(self):
        return self.config.load_friends()

    def get_user_profile(self, account_id, user=None):
        """
        Return the profile of the *user*, using the *account_id*,
        if user is None, it returns the profile of account_id itself.
        """
        account = self.accman.get(account_id)
        if user:
            profile = account.get_profile(user)
            profile.followed_by = account.is_friend(user)
            profile.muted = self.is_muted(profile.username)
        else:
            profile = account.profile
        return profile

    def get_conversation(self, account_id, status_id):
        account = self.accman.get(account_id)
        return account.get_conversation(status_id)

    def update_status(self, account_id, text, in_reply_id=None, media=None):
        """
        Updates the account *account_id* with content of *text*

        if *in_reply_id* is not None, specifies the tweets that is being answered.

        *media* can specify the filepath of an image. If not None, the status is posted with
        the image attached. At this moment, this method is only valid for Twitter.
        """
        account = self.accman.get(account_id)
        return account.update_status(text, in_reply_id, media)

    def broadcast_status(self, account_id_array, text):
        """
        Updates all the accounts in account_id_array with the content of *text*

        if account_id_array is None or an empty list all registered accounts
        get updated.
        """
        if not account_id_array:
            account_id_array = [acc.id_ for acc in self.registered_accounts()]

        response = {}
        for account_id in account_id_array:
            try:
                account = self.accman.get(account_id)
                response[account_id] = account.update_status(text)
            except Exception, exc:
                response[account_id] = exc
        return response

    def destroy_status(self, account_id, status_id):
        """
        Deletes status of *account_id* specified by *status_id*
        """
        account = self.accman.get(account_id)
        return account.destroy_status(status_id)

    def get_single_status(self, account_id, status_id):
        """
        Retrieves a single status with *account_id* that corresponds with *status_id*
        """
        account = self.accman.get(account_id)
        return account.get_status(status_id)

    def repeat_status(self, account_id, status_id):
        """
        Allows to send the same status again by using repeat option in API
        """
        account = self.accman.get(account_id)
        return account.repeat_status(status_id)

    def mark_status_as_favorite(self, account_id, status_id):
        """
        Marks status of *account_id* specified by *status_id* as favorite
        """
        account = self.accman.get(account_id)
        return account.mark_as_favorite(status_id)

    def unmark_status_as_favorite(self, account_id, status_id):
        """
        Unmarks status of *account_id* specified by *status_id* as favorite
        """
        account = self.accman.get(account_id)
        return account.unmark_as_favorite(status_id)

    def send_direct_message(self, account_id, username, message):
        """
        Sends a direct update with the contant of *message* to *username* using *account_id*
        """
        account = self.accman.get(account_id)
        return account.send_direct_message(username, message)

    def destroy_direct_message(self, account_id, status_id):
        """
        Deletes a direct update from *account_id* defined by its *status_id*
        """
        account = self.accman.get(account_id)
        return account.destroy_direct_message(status_id)

    # TODO: Validate at least one of the parameters
    def update_profile(self, account_id, fullname=None, url=None, bio=None,
            location=None):
        """
        Updates the *account_id* public profile with the information in variables
        fullname = Complete account name
        url = Blog or personal URL of the account
        bio = Small resume
        location = Geographic location
        """
        account = self.accman.get(account_id)
        return account.update_profile(fullname, url, bio, location)

    def follow(self, account_id, username, by_id=False):
        """
        Makes *account_id* a follower of *username*.
        Return a :class:`libturpial.api.models.profile.Profile` object with the user profile
        """
        account = self.accman.get(account_id)
        response = account.follow(username, by_id)
        self.add_friend(username)
        return response

    def unfollow(self, account_id, username):
        """
        Stops *account_id* from being a follower of *username*.
        Return a :class:`libturpial.api.models.profile.Profile` object with the user profile
        """
        account = self.accman.get(account_id)
        response = account.unfollow(username)
        self.remove_friend(username)
        return response

    def block(self, account_id, username):
        """
        Blocks *username* in *account_id*.
        Return a :class:`libturpial.api.models.profile.Profile` object with the user profile
        """
        account = self.accman.get(account_id)
        response = account.block(username)
        self.remove_friend(username)
        return response

    def unblock(self, account_id, username):
        """
        Unblocks *username* in *account_id*.
        Return a :class:`libturpial.api.models.profile.Profile` object with the user profile
        """
        account = self.accman.get(account_id)
        return account.unblock(username)

    def report_as_spam(self, account_id, username):
        """
        Reports *username* as SPAM using *account_id*.
        Return a :class:`libturpial.api.models.profile.Profile` object with the user profile
        """
        account = self.accman.get(account_id)
        response = account.report_as_spam(username)
        self.remove_friend(username)
        return response

    def mute(self, username):
        """
        Adds *username* into the muted list, so that no more statuses from
        that account are shown
        """
        self.config.append_filter('@%s' % username)
        return username

    def unmute(self, username):
        """
        Removes *username* from the muted list, so that statuses from
        that account are now shown
        """
        self.config.remove_filter('@%s' % username)
        return username

    def verify_friendship(self, account_id, username):
        """
        Return *True* if the owner of *account_id* and *username* are following each other.
        *False* otherwise.
        """
        account = self.accman.get(account_id)
        return account.is_friend(username)

    def search(self, account_id, query, count=NUM_STATUSES, since_id=None, extra=None):
        """
        Performs a search using Twitter API, defined by:
        account_id = Account to be used for the search
        query = Search Term
        acount = Max number of results
        since_id = if limited to a status id and on.
        """
        account = self.accman.get(account_id)
        # The unquote is to ensure that the query is not url-encoded. The
        # encoding will be done automatically by the http module
        unquoted_query = urllib2.unquote(query)
        return account.search(unquoted_query, count, since_id, extra)

    def get_profile_image(self, account_id, username, use_cache=True):
        """
        Return the local path to a the profile image of *username* in original size.
        If use_cache is *True* it will try to return the cached file, otherwise it
        will fetch the real image.
        """
        account = self.accman.get(account_id)
        basename = "%s-%s-profile-image" % (account_id, username)
        img_destination_path = os.path.join(account.config.imgdir, basename)
        if not os.path.isfile(img_destination_path) or use_cache == False:
            img_url = account.get_profile_image(username)
            fd = open(img_destination_path, 'w')
            fd.write(self.fetch_image(img_url))
            fd.close()
        return img_destination_path

    def get_status_avatar(self, status):
        """
        Return the local path to a the profile image of the username to post *status* in 48x48 px size
        """
        account = self.accman.get(status.account_id)
        basename = "%s-%s-avatar-%s" % (status.account_id, status.username, os.path.basename(status.avatar))
        img_destination_path = os.path.join(account.config.imgdir, basename)
        if not os.path.isfile(img_destination_path):
            fp = open(img_destination_path, 'w')
            fp.write(self.fetch_image(status.avatar))
            fp.close()
        return img_destination_path

    def get_available_trend_locations(self, account_id):
        """
        Return an array of :class:`libturpial.api.models.trend.TrendLocation` objects with all the
        locations with trending topics registered.
        """
        account = self.accman.get(account_id)
        return account.available_trend_locations()

    def get_trending_topics(self, account_id, location_id):
        """
        Return an array of :class:`libturpial.api.models.trend.Trend` objects with trending topics
        for the specified location. *location_id* is the Yahoo! Where On Earth ID for the location.
        """
        account = self.accman.get(account_id)
        return account.trends(location_id)

    def update_profile_image(self, account_id, image_path):
        """
        Update profile image of *account_id* with the image specified by *image_path*.
        Return a :class:`libturpial.api.models.profile.Profile` object
        with the user profile updated.
        """
        account = self.accman.get(account_id)
        return account.update_profile_image(image_path)

    ###########################################################################
    # Services API
    ###########################################################################

    def available_short_url_services(self):
        return URL_SERVICES.keys()

    def short_single_url(self, long_url):
        service = self.get_shorten_url_service()
        if os.path.split(long_url)[0].find(service) >= 0:
            raise URLAlreadyShort
        urlshorter = self.__get_short_url_object(service)
        return urlshorter.do_service(long_url)

    def short_url_in_message(self, message):
        all_urls = get_urls(message)
        if len(all_urls) == 0:
            raise NoURLToShorten

        for long_url in all_urls:
            try:
                short_url = self.short_single_url(long_url)
            except URLAlreadyShort:
                short_url = long_url
            finally:
                message = message.replace(long_url, short_url)
        return message

    def available_preview_media_services(self):
        return PREVIEW_MEDIA_SERVICES.keys()

    def preview_media(self, url):
        if not is_preview_service_supported(url):
            raise PreviewServiceNotSupported

        service = get_preview_service_from_url(url)
        return service.do_service(url)

    def available_upload_media_services(self):
        return UPLOAD_MEDIA_SERVICES.keys()

    def upload_media(self, account_id, filepath, message=None):
        service = self.get_upload_media_service()
        account = self.accman.get(account_id)
        uploader = self.__get_upload_media_object(service)
        return uploader.do_service(account, filepath, message)

    ###########################################################################
    # Configuration API
    ###########################################################################

    # TODO: Return added option?
    def register_new_config_option(self, section, option, default_value):
        """
        Register a new configuration *option* in *section* to be handled by
        external modules. libturpial will set *default_value* as value if
        the option doesn't exist.

        This method should be used if a module that uses libturpial needs to
        handle configuration options not registered by default.

        For example, if you want to register an option to handle notifications
        on login the code should looks like:

        >>> core = Core()
        >>> core.register_new_config_option('Notifications', 'login', 'on')

        From this point you can use config methods over this value as usual.
        """
        self.config.register_extra_option(section, option, default_value)

    def get_shorten_url_service(self):
        return self.config.read('Services', 'shorten-url')

    def get_upload_media_service(self):
        return self.config.read('Services', 'upload-pic')

    def set_shorten_url_service(self, value):
        return self.config.write('Services', 'shorten-url', value)

    def set_upload_media_service(self, value):
        return self.config.write('Services', 'upload-pic', value)

    # WARN: Will be deprecated on next mayor version
    def has_stored_passwd(self, account_id):
        account = self.accman.get(account_id)
        if account.profile.password is None:
            return False
        if account.profile.password == '':
            return False
        return True

    # WARN: Will be deprecated on next mayor version
    def is_account_logged_in(self, account_id):
        account = self.accman.get(account_id)
        return account.logged_in

    def is_muted(self, username):
        """
        Return *True* is *username* is muted. *False* otherwise
        """
        filtered_terms = self.config.load_filters()
        for term in filtered_terms:
            if not term.startswith('@'):
                continue

            if username == term[1:]:
                return True
        return False

    # WARN: Will be deprecated on next mayor version
    def get_default_browser(self):
        return self.config.read('Browser', 'cmd')

    # WARN: Will be deprecated on next mayor version
    def show_notifications_in_login(self):
        temp = self.config.read('Notifications', 'login')
        if temp == 'on':
            return True
        return False

    # WARN: Will be deprecated on next mayor version
    def show_notifications_in_updates(self):
        temp = self.config.read('Notifications', 'updates')
        if temp == 'on':
            return True
        return False

    # WARN: Will be deprecated on next mayor version
    def play_sounds_in_login(self):
        temp = self.config.read('Sounds', 'login')
        if temp == 'on':
            return True
        return False

    # WARN: Will be deprecated on next mayor version
    def play_sounds_in_updates(self):
        temp = self.config.read('Sounds', 'updates')
        if temp == 'on':
            return True
        return False

    def get_max_statuses_per_column(self):
        """
        Return how many statuses should be fetched in each requests
        """
        return int(self.config.read('General', 'statuses'))

    def get_proxy(self):
        """
        Return a :class:`libturpial.api.models.proxy.Proxy` object with
        the configuration stored in disk.
        """
        return self.config.get_proxy()

    def get_socket_timeout(self):
        """
        Return the timeout set for the socket connections
        """
        return int(self.config.get_socket_timeout())

    # WARN: Will be deprecated on next mayor version
    def get_update_interval(self):
        return int(self.config.read('General', 'update-interval'))

    # WARN: Will be deprecated on next mayor version
    def minimize_on_close(self):
        minimize = self.config.read('General', 'minimize-on-close')
        return True if minimize == 'on' else False

    # WARN: Will be deprecated on next mayor version
    def get_config(self):
        return self.config.read_all()

    # WARN: Will be deprecated on next mayor version
    def read_config_value(self, section, option):
        return self.config.read(section, option)

    # WARN: Will be deprecated on next mayor version
    def write_config_value(self, section, option, value):
        self.config.write(section, option, value)

    # WARN: Will be deprecated on next mayor version
    def save_all_config(self, new_config):
        self.config.save(new_config)

    def list_filters(self):
        """
        Return a list with all registered filters
        """
        return self.config.load_filters()

    # TODO: Return saved filters or True
    def save_filters(self, lst):
        """
        Save *lst* a the new filters list
        """
        self.config.save_filters(lst)

    # TODO: Return True on success
    def delete_current_config(self):
        """
        Delete current configuration file. This action can not be undone
        """
        self.config.delete()

    # TODO: Return True on success
    def delete_cache(self):
        """
        Delete all files in cache
        """
        for account in self.registered_accounts():
            account.delete_cache()

    def get_cache_size(self):
        """
        Return current space used by cache
        """
        total_size = 0
        for account in self.registered_accounts():
            total_size += account.get_cache_size()
        return total_size

    # TODO: Return added friend
    def add_friend(self, username):
        """
        Save *username* into the friends list
        """
        friends = self.config.load_friends()
        friends.append(username)
        self.config.save_friends(friends)

    # TODO: Return removed friend
    def remove_friend(self, username):
        """
        Remove *username* from friends list
        """
        friends = self.config.load_friends()
        if username in friends:
            friends.remove(username)
            self.config.save_friends(friends)
