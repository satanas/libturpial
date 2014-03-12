# -*- coding: utf-8 -*-

""" Identi.ca implementation for Turpial"""

import re

from libturpial.api.models.status import Status
from libturpial.api.models.entity import Entity
from libturpial.api.models.profile import Profile

from libturpial.lib.interfaces.protocol import Protocol
from libturpial.lib.http import TurpialHTTPBasicAuth
from libturpial.common import NUM_STATUSES, StatusColumn
from libturpial.exceptions import *

# TODO:
# * Change for loops for list comprehension

class Main(Protocol):
    """Identi.ca implementation for libturpial"""
    GROUP_PATTERN = re.compile('(?<![\w])![\wáéíóúÁÉÍÓÚñÑçÇ]+')

    def __init__(self):
        self.uname = None
        self.base_url = 'https://identi.ca/api'
        self.search_url = 'http://identi.ca/api'
        self.hashtags_url = 'http://identi.ca/tag'
        self.profiles_url = 'http://identi.ca'
        self.groups_url = 'http://identi.ca/group'

        Protocol.__init__(self)

    def __build_basic_args(self, count, since_id):
        args = {'count': count, 'include_entities': True}
        if since_id:
            args['since_id'] = since_id
        return args

    def check_for_errors(self, response):
        """
        Receives a json response and raise an exception if there are errors
        """
        if 'error' in response:
            print response
            message = response['error']
            if message.find('Could not authenticate you') >= 0:
                raise InvalidOrMissingCredentials
            elif message.find('duplicated messages') > 0:
                raise StatusDuplicated
            elif message.find("to users who aren't your friend") > 0:
                raise ErrorSendingDirectMessage('User is not following you')
            elif message.find('Maximum notice size is 140 characters') > 0:
                raise StatusMessageTooLong

            #elif code == 34 or code == 404:
            #    raise ResourceNotFound
            #elif code == 64:
            #    raise AccountSuspended
            #elif code == 88:
            #    raise RateLimitExceeded
            #elif code == 89:
            #    raise InvalidOAuthToken
            #elif code == 130 or code == 503 or code == 504:
            #    raise ServiceOverCapacity
            #elif code == 131 or code == 500:
            #    raise InternalServerError
            #elif code == 135:
            #    raise BadOAuthTimestamp
            #elif code == 502:
            #    raise ServiceDown

    def initialize_http(self):
        self.http = TurpialHTTPBasicAuth(self.base_url)

    def setup_user_credentials(self, account_id, username, password):
        self.account_id = account_id
        self.http.set_user_info(username, password)
        self.uname = account_id.split('-')[0]


    #################################################################
    # Methods related to Twitter service
    #################################################################

    def verify_credentials(self):
        rtn = self.http.get('/account/verify_credentials', secure=True)
        self.check_for_errors(rtn)
        profile = self.json_to_profile(rtn)
        self.uname = profile.username
        return profile


    def get_timeline(self, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        rtn = self.http.get('/statuses/home_timeline', args)
        self.check_for_errors(rtn)
        return self.json_to_status(rtn, StatusColumn.TIMELINE)

    def get_replies(self, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        rtn = self.http.get('/statuses/mentions', args)
        self.check_for_errors(rtn)
        return self.json_to_status(rtn, StatusColumn.REPLIES)

    def get_directs(self, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        rtn = self.http.get('/direct_messages', args)
        self.check_for_errors(rtn)
        return self.json_to_status(rtn, StatusColumn.DIRECTS,
                                   type_=Status.DIRECT)

    def get_directs_sent(self, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        rtn = self.http.get('/direct_messages/sent', args)
        self.check_for_errors(rtn)
        return self.json_to_status(rtn, StatusColumn.DIRECTS,
                                   type_=Status.DIRECT)

    def get_sent(self, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        rtn = self.http.get('/statuses/user_timeline', args)
        self.check_for_errors(rtn)
        return self.json_to_status(rtn, StatusColumn.SENT)

    def get_favorites(self, count=NUM_STATUSES):
        rtn = self.http.get('/favorites')
        self.check_for_errors(rtn)
        return self.json_to_status(rtn, StatusColumn.FAVORITES)

    def get_public_timeline(self, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        rtn = self.http.get('/statuses/public_timeline', args)
        self.check_for_errors(rtn)
        return self.json_to_status(rtn, StatusColumn.PUBLIC)

    def get_lists(self, username):
        return []

    def get_list_statuses(self, list_id, user, count=NUM_STATUSES, since_id=None):
        return []

    def get_conversation(self, status_id):
        conversation = []

        while 1:
            rtn = self.http.get('/statuses/show', {'id': status_id})
            conversation.append(self.json_to_status(rtn,
                                StatusColumn.CONVERSATION))

            if rtn['in_reply_to_status_id']:
                status_id = str(rtn['in_reply_to_status_id'])
            else:
                break
        return conversation

    def get_status(self, status_id):
        rtn = self.http.get('/statuses/show', {'id': status_id})
        self.check_for_errors(rtn)
        return self.json_to_status(rtn)

    def get_followers(self, only_id=False):
        followers = []

        if only_id:
            rtn = self.http.get('/followers/ids')
            for id_ in rtn:
                followers.append(str(id_))
        else:
            rtn = self.http.get('/statuses/followers',
                               {'screen_name': self.account_id.split('-')[0]})
            for user in rtn:
                followers.append(self.json_to_profile(user))

        return followers

    def get_following(self, only_id=False):
        following = []

        if only_id:
            rtn = self.http.get('/friends/ids')
            for id_ in rtn:
                following.append(str(id_))
        else:
            rtn = self.http.get('/statuses/friends',
                               {'screen_name': self.account_id.split('-')[0]})
            following = [self.json_to_profile(user) for user in rtn]

        return following

    def get_profile(self, user):
        rtn = self.http.get('/users/show', {'screen_name': user})
        self.check_for_errors(rtn)
        profile = self.json_to_profile(rtn)
        rtn = self.http.get('/statuses/user_timeline',
                           {'screen_name': user, 'count': 10})
        profile.recent_updates = self.json_to_status(rtn)
        return profile

    def get_blocked(self):
        return []

    def get_rate_limits(self):
        rtn = self.http.get('/account/rate_limit_status')
        self.check_for_errors(rtn)
        return self.json_to_ratelimit(rtn)

    def update_profile(self, p_args):
        # We use if's instead update method to guarantee valid arguments
        args = {}
        if 'name' in p_args:
            args['name'] = p_args['name']
        if 'url' in p_args:
            args['url'] = p_args['url']
        if 'description' in p_args:
            args['description'] = p_args['description']
        if 'location' in p_args:
            args['location'] = p_args['location']

        rtn = self.http.post('/account/update_profile', args, secure=True)
        self.check_for_errors(rtn)
        return self.json_to_profile(rtn)

    def update_status(self, text, in_reply_id=None):
        if in_reply_id:
            args = {'status': text, 'in_reply_to_status_id': in_reply_id}
        else:
            args = {'status': text}

        rtn = self.http.post('/statuses/update', args, secure=True)
        self.check_for_errors(rtn)
        return self.json_to_status(rtn)

    def destroy_status(self, status_id):
        rtn = self.http.post('/statuses/destroy', {'id': status_id}, secure=True)
        self.check_for_errors(rtn)
        return self.json_to_status(rtn)

    def repeat_status(self, status_id):
        rtn = self.http.post('/statuses/retweet', {'id': status_id}, secure=True)
        self.check_for_errors(rtn)
        status = self.json_to_status(rtn)
        return status

    def mark_as_favorite(self, status_id):
        rtn = self.http.post('/favorites/create', {'id': status_id}, secure=True)
        self.check_for_errors(rtn)
        return self.json_to_status(rtn)

    def unmark_as_favorite(self, status_id):
        rtn = self.http.post('/favorites/destroy', {'id': status_id}, secure=True)
        self.check_for_errors(rtn)
        return self.json_to_status(rtn)

    def follow(self, screen_name, by_id=False):
        if by_id:
            arg = {'user_id': screen_name}
        else:
            arg = {'screen_name': screen_name}
        rtn = self.http.post('/friendships/create', arg, secure=True)
        self.check_for_errors(rtn)
        return self.json_to_profile(rtn)

    def unfollow(self, screen_name):
        rtn = self.http.post('/friendships/destroy',
                           {'screen_name': screen_name}, secure=True)
        self.check_for_errors(rtn)
        return self.json_to_profile(rtn)

    def send_direct_message(self, screen_name, text):
        args = {'screen_name': screen_name, 'text': text}
        rtn = self.http.post('/direct_messages/new', args, secure=True)
        self.check_for_errors(rtn)
        return self.json_to_status(rtn)

    def destroy_direct_message(self, direct_message_id):
        return None


    def block(self, screen_name):
        rtn = self.http.post('/blocks/create', {'screen_name': screen_name}, secure=True)
        self.check_for_errors(rtn)
        return self.json_to_profile(rtn)

    def unblock(self, screen_name):
        rtn = self.http.post('/blocks/destroy', {'screen_name': screen_name}, secure=True)
        self.check_for_errors(rtn)
        return self.json_to_profile(rtn)

    def search(self, query, count=NUM_STATUSES, since_id=None):
        rtn = self.http.get('/search', {'q': query, 'rpp': count},
                           base_url=self.urls['search'])
        self.check_for_errors(rtn)
        return self.json_to_status(rtn['results'])

    def is_friend(self, user):
        args = {'source_screen_name': self.uname, 'target_screen_name': user}
        result = self.http.get('/friendships/show', args)
        if 'error' in result:
            return None
        else:
            return result['relationship']['target']['following']

    def get_profile_image(self, user):
        result = self.http.get('/users/show', {'screen_name': user})
        return rtn['profile_image_url']

    #################################################################
    # Methods to convert JSON responses into objects
    #################################################################

    # TODO: Try to do this with metaprogramming (a single JSON object that
    # knows how to become a turpial object

    def json_to_profile(self, response):
        if isinstance(response, list):
            profiles = []
            for pf in response:
                profile = self.json_to_profile(json_to_profile)
                profiles.append(profile)
            return profiles
        else:
            profile = Profile()
            profile.id_ = str(response['id'])
            profile.account_id = self.account_id
            profile.fullname = response['name']
            profile.username = response['screen_name']
            profile.avatar = response['profile_image_url']
            profile.location = response['location']
            profile.url = response['url']
            profile.bio = response['description']
            profile.following = response['following']
            profile.followers_count = response['followers_count']
            profile.friends_count = response['friends_count']
            profile.statuses_count = response['statuses_count']
            profile.favorites_count = response['favourites_count']
            profile.protected = response['protected']
            if 'status' in response:
                profile.last_update = response['status']['text']
                profile.last_update_id = response['status']['id']
            #profile.link_color = Profile.DEFAULT_LINK_COLOR
            return profile

    def json_to_status(self, response, column_id='', type_=Status.NORMAL):
        if isinstance(response, list):
            statuses = []
            for resp in response:
                if not resp:
                    continue
                status = self.json_to_status(resp, column_id, type_)
                statuses.append(status)
            return statuses
        else:
            reposted_by = None
            if 'retweeted_status' in response:
                reposted_by = response['user']['screen_name']
                post = response['retweeted_status']
            else:
                post = response

            protected = False
            if 'user' in post:
                username = post['user']['screen_name']
                avatar = post['user']['profile_image_url']
                protected = post['user']['protected']
            elif 'sender' in post:
                username = post['sender']['screen_name']
                avatar = post['sender']['profile_image_url']
                protected = post['sender']['protected']
            elif 'from_user' in post:
                username = post['from_user']
                avatar = post['profile_image_url']

            in_reply_to_id = None
            in_reply_to_user = None
            if 'in_reply_to_status_id' in post and post['in_reply_to_status_id']:
                in_reply_to_id = post['in_reply_to_status_id']
                in_reply_to_user = post['in_reply_to_screen_name']

            fav = False
            if 'favorited' in post:
                fav = post['favorited']

            source = None
            if 'source' in post:
                source = post['source']

            status = Status()
            status.id_ = str(post['id'])
            status.username = username
            status.avatar = avatar
            status.text = post['text']
            status.in_reply_to_id = in_reply_to_id
            status.in_reply_to_user = in_reply_to_user
            status.is_favorite = fav
            status.is_protected = protected
            status.is_verified = False
            status.reposted_by = reposted_by
            status.datetime = self.get_str_time(post['created_at'])
            status.timestamp = self.get_int_time(post['created_at'])
            status.entities = self.get_entities(post)
            status.type_ = type_
            status.account_id = self.account_id
            status.is_own = (username.lower() == self.uname.lower())
            status.set_display_id(column_id)
            status.get_source(source)
            return status

    def get_entities(self, status):
        entities = Protocol.get_entities(self, status)
        for item in self.GROUP_PATTERN.findall(status['text']):
            url = "%s/%s" % (self.groups_url, item[1:])
            entities['groups'].append(Entity(self.account_id, url, item, item))
        return entities
