# -*- coding: utf-8 -*-

"""Generic module to implement microblogging protocols in Turpial"""

import time
import logging
import datetime

from libturpial.common import *
from libturpial.common.tools import *
from libturpial.exceptions import NotSupported
from libturpial.api.models.entity import Entity
from libturpial.lib.http import TurpialHTTPBase


class Protocol:
    """
    Bridge class to define abstract functions that must have any protocol
    implementation
    """
    TWITTER = 'twitter'
    IDENTICA = 'identica'

    def __init__(self):
        self.account_id = None
        self.initialize_http()

        self.log = logging.getLogger('change me')
        self.log.debug('Started')

    @staticmethod
    def availables():
        return [Protocol.TWITTER, Protocol.IDENTICA]

    # ------------------------------------------------------------
    # Time related methods. Overwrite if necesary
    # libturpial handles all timestamps in GMT-0
    # ------------------------------------------------------------
    def convert_time(self, str_datetime):
        """
        Takes the *str_datetime* and convert it into Unix time
        """
        # Tue Mar 13 00:12:41 +0000 2007 -> Tweets normales
        # Wed, 08 Apr 2009 19:22:10 +0000 -> Busquedas
        month_names = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                       'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        date_info = str_datetime.split()

        if date_info[1] in month_names:
            month = month_names.index(date_info[1])
            day = int(date_info[2])
            year = int(date_info[5])
            time_info = date_info[3].split(':')
        else:
            month = month_names.index(date_info[2])
            day = int(date_info[1])
            year = int(date_info[3])
            time_info = date_info[4].split(':')

        hour = int(time_info[0])
        minute = int(time_info[1])
        second = int(time_info[2])

        d = datetime.datetime(year, month, day, hour, minute, second)
        return d.timetuple()

    def get_str_time(self, strdate):
        """
        Converts the *strdate* into a formatted string (GMT 0)
        """
        t = self.convert_time(strdate)
        return time.strftime('%b %d, %I:%M %p', t)

    def get_int_time(self, strdate):
        """
        Converts the *strdate* into a Unix time long integer (GMT 0)
        """
        t = self.convert_time(strdate)
        return time.mktime(t)

    def get_entities(self, status):
        entities = {
            'urls': [],
            'hashtags': [],
            'mentions': [],
            'groups': [],
        }
        text = status['text']

        for url in get_urls(text):
            entities['urls'].append(Entity(self.account_id, url, url, url))

        for item in HASHTAG_PATTERN.findall(text):
            url = "%s/%s" % (self.hashtags_url, item[1:])
            entities['hashtags'].append(Entity(self.account_id, url, item, item))

        for item in MENTION_PATTERN.findall(text):
            entities['mentions'].append(Entity(self.account_id, item[1:], item, item))
        return entities

    # ------------------------------------------------------------
    # Methods to be overwritten
    # ------------------------------------------------------------

    def initialize_http(self):
        """
        Creates a new TurpialHTTP instance that must be stored in self.http

        For OAuth do:

        >>> self.http = TurpialHTTPOAuth(base_url, oauth_options, proxies, timeout)

        For Basic Auth do:

        >>> self.http = TurpialHTTPBasicAuth(base_url, proxies, timeout)
        """
        raise NotImplementedError


    def request_access(self):
        """
        Return an OAuth authorization URL. Do not overide if the protocol
        does not support OAuth
        """
        raise NotSupported

    def setup_user_credentials(self):
        """
        Set the information related to user credentials. *key*, *secret* and
        *verifier* for the OAuth case and *username*, *password* in the Basic
        case
        """

    def json_to_profile(self, response):
        """
        Takes a JSON *response* and returns a
        :class:`libturpial.api.models.profile.Profile` object

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def json_to_status(self, response):
        """
        Takes a JSON *response* and returns a
        :class:`libturpial.api.models.status.Status` object

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def json_to_ratelimit(self, response):
        """
        Takes a JSON *response* and returns a
        :class:`libturpial.api.models.ratelimit.RateLimit` object

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def json_to_list(self, response):
        """
        Takes a JSON *response* and returns a
        :class:`libturpial.api.models.list.List` object

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def verify_credentials(self):
        raise NotImplementedError

    def verify_credentials_provider(self):
        # Must return URL of the verify_credentials provider
        raise NotImplementedError

    def get_timeline(self, count, since_id):
        """
        Fetch *count* statuses from timeline starting from *since_id*. If
        *since_id* is None it will fetch the last *count* statuses

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_replies(self, count, since_id):
        """
        Fetch *count* mentions starting from *since_id*. If *since_id* is None
        it will fetch the last *count* statuses

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_directs(self, count, since_id):
        """
        Fetch *count* direct messages received starting from *since_id*. If
        *since_id* is None it will fetch the last *count* statuses

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_directs_sent(self, count, since_id):
        """
        Fetch *count* direct messages sent starting from *since_id*. If
        *since_id* is None it will fetch the last *count* statuses

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_sent(self, count, since_id):
        """
        Fetch *count* sent statuses starting from *since_id*. If *since_id* is
        None it will fetch the last *count* statuses

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_favorites(self, count):
        """
        Fetch *count* favorite statuses starting from *since_id*. If *since_id*
        is None it will fetch the last *count* statuses

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_public_timeline(self, count, since_id):
        """
        Fetch *count* statuses from public timeline starting from *since_id*.
        If *since_id* is None it will fetch the last *count* statuses

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_lists(self, username):
        """
        Fetch all the lists where *username* is part of

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_list_statuses(self, list_id, since_id):
        """
        Fetch all statuses from *list_id* starting from *since_id*. If
        *since_id* is None it will fetch the last available statuses

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_conversation(self, status_id):
        """
        Fetch a whole conversation starting from *status_id*

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_status(self, status_id):
        """
        Fetch the status identified by *status_id*

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_followers(self, only_id=False):
        """
        Fetch an array of :class list of followers

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_following(self, only_id=False):
        """
        Fetch the list of following

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_profile(self, user):
        """
        Fetch an especific user profile

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_blocked(self):
        """
        Fetch the list of blocked users

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_rate_limits(self):
        """
        Fetch the rate limits for the service

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_repeaters(self, status_id, only_username=False):
        """
        Fetch all the users that repeated *status_id*

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def update_profile(self, fullname=None, url=None, bio=None, location=None):
        """
        Update the user profile

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def update_status(self, text, in_reply_to_id=None, media=None):
        """
        Post an update

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def destroy_status(self, status_id):
        """
        Destroy a posted update

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def repeat_status(self, status_id):
        """
        Repeat to all your friends an update posted by somebody

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def mark_as_favorite(self, status_id):
        """
        Mark an update as favorite

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def unmark_as_favorite(self, status_id):
        """
        Unmark an update as favorite

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def follow(self, user, by_id):
        """
        Follow somebody

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def unfollow(self, user):
        """
        Unfollow somebody

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def send_direct_message(self, user, text):
        # FIXME: Implementar
        #raise NotImplementedError
        pass

    def destroy_direct_message(self, direct_message_id):
        """
        Destroy a direct message

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def block(self, user):
        """
        Blocks the specified user

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def unblock(self, user):
        """
        Unblocks the specified user

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def report_as_spam(self, user):
        """
        Blocks and report the specified user as spammer

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def search(self, query, count, since_id=None, extra=None):
        """
        Execute a search query in server

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def is_friend(self, user):
        """
        Returns True is user follows current account, False otherwise

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def get_profile_image(self, user):
        """
        Returns the URL for the profile image of the given user

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def trends(self, location_id):
        """
        Search for trending topics in *location_id*

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def available_trend_locations(self):
        """
        Search for trend locations

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError

    def update_profile_image(self, image_path):
        """
        Update user profile image and return user profile object

        .. warning::
            This is an empty method and must be reimplemented on child class,
            otherwise it will raise a **NotImplementedError** exception
        """
        raise NotImplementedError
