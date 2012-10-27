# -*- coding: utf-8 -*-

""" Identi.ca implementation for Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Jun 08, 2010

import re
import base64

from libturpial.common import *
from libturpial.api.models.entity import Entity
from libturpial.api.models.status import Status
from libturpial.api.models.profile import Profile
from libturpial.api.interfaces.protocol import Protocol
from libturpial.api.protocols.identica.params import CK, CS, SALT, POST_ACTIONS


class Main(Protocol):
    """Identi.ca implementation for libturpial"""
    GROUP_PATTERN = re.compile('(?<![\w])![\wáéíóúÁÉÍÓÚñÑçÇ]+')

    def __init__(self, username, account_id, auth):
        p_name = 'Identi.ca(%s)' % username
        Protocol.__init__(self, account_id, p_name,
                          'https://identi.ca/api',
                          'http://identi.ca/api',
                          'http://identi.ca/tag',
                          'http://identi.ca/group',
                          'http://identi.ca',
                          POST_ACTIONS)

        self.REQUEST_TOKEN_URL = 'https://identi.ca/api/oauth/request_token'
        self.ACCESS_TOKEN_URL = 'https://identi.ca/api/oauth/access_token'
        self.AUTHORIZATION_URL = 'https://identi.ca/api/oauth/authorize'

        self.oauth_support = False
        self.uname = None
        self.set_consumer(CK, base64.b64decode(CS + SALT))
        if auth:
            self.set_auth_info(auth)

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
            profile.link_color = Profile.DEFAULT_LINK_COLOR
            return profile

    def json_to_status(self, response, column_id='', _type=StatusType.NORMAL):
        if isinstance(response, list):
            statuses = []
            for resp in response:
                if not resp:
                    continue
                status = self.json_to_status(resp, column_id, _type)
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
            status.source = self.get_source(source)
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
            status._type = _type
            status.account_id = self.account_id
            status.is_own = (username.lower() == self.uname.lower())
            status.set_display_id(column_id)
            return status

    def auth(self, username, password):
        self.log.debug('Starting auth')
        if not self.oauth_support:
            self.set_auth_info({'username': username, 'password': password})
        rtn = self.request('/account/verify_credentials', secure=True)
        profile = self.json_to_profile(rtn)
        self.uname = profile.username
        return profile

    def get_entities(self, status):
        entities = Protocol.get_entities(self, status)
        for item in self.GROUP_PATTERN.findall(status['text']):
            url = "%s/%s" % (self.urls['groups'], item[1:])
            entities['groups'].append(Entity(url, item, item))
        return entities

    def get_timeline(self, count=STATUSPP, since_id=None):
        self.log.debug('Getting timeline')
        rtn = self.request('/statuses/home_timeline',
                           {'count': count, 'since_id': since_id})
        return self.json_to_status(rtn, StatusColumn.TIMELINE)

    def get_replies(self, count=STATUSPP, since_id=None):
        self.log.debug('Getting replies')
        rtn = self.request('/statuses/mentions', {'count': count})
        return self.json_to_status(rtn, StatusColumn.REPLIES)

    def get_directs(self, count=STATUSPP, since_id=None):
        self.log.debug('Getting directs')
        rtn = self.request('/direct_messages', {'count': count})
        return self.json_to_status(rtn, StatusColumn.DIRECTS,
                                   _type=StatusType.DIRECT)

    def get_directs_sent(self, count=STATUSPP, since_id=None):
        self.log.debug('Getting directs sent')
        rtn = self.request('/direct_messages/sent', {'count': count})
        return self.json_to_status(rtn, StatusColumn.DIRECTS,
                                   _type=StatusType.DIRECT)

    def get_sent(self, count=STATUSPP, since_id=None):
        self.log.debug('Getting my statuses')
        rtn = self.request('/statuses/user_timeline', {'count': count})
        return self.json_to_status(rtn, StatusColumn.SENT)

    def get_favorites(self, count=STATUSPP):
        self.log.debug('Getting favorites')
        rtn = self.request('/favorites')
        return self.json_to_status(rtn, StatusColumn.FAVORITES)

    def get_public_timeline(self, count=STATUSPP, since_id=None):
        self.log.debug('Getting public timeline')
        rtn = self.request('/statuses/public_timeline', {'count': count,
                           'include_entities': True})
        return self.json_to_status(rtn, StatusColumn.PUBLIC)

    def get_lists(self, username):
        return []

    def get_list_statuses(self, list_id, user, count=STATUSPP, since_id=None):
        pass

    def get_conversation(self, status_id):
        self.log.debug('Getting conversation for status %s' % status_id)
        conversation = []

        while 1:
            rtn = self.request('/statuses/show', {'id': status_id})
            self.log.debug('--Fetched status: %s' % status_id)
            conversation.append(self.json_to_status(rtn,
                                StatusColumn.CONVERSATION))

            if rtn['in_reply_to_status_id']:
                status_id = str(rtn['in_reply_to_status_id'])
            else:
                break
        return conversation

    def get_status(self, status_id):
        rtn = self.request('/statuses/show', {'id': status_id})
        return self.json_to_status(rtn)

    def get_followers(self, only_id=False):
        self.log.debug('Getting followers list')
        followers = []

        if only_id:
            rtn = self.request('/followers/ids')
            for id_ in rtn:
                followers.append(str(id_))
        else:
            rtn = self.request('/statuses/followers',
                               {'screen_name': self.account_id.split('-')[0]})
            for user in rtn:
                followers.append(self.json_to_profile(user))

        self.log.debug('--Downloaded %i followers' % len(followers))
        return followers

    def get_following(self, only_id=False):
        self.log.debug('Getting following list')
        following = []

        if only_id:
            rtn = self.request('/friends/ids')
            for id_ in rtn:
                following.append(str(id_))
        else:
            rtn = self.request('/statuses/friends',
                               {'screen_name': self.account_id.split('-')[0]})
            for user in rtn:
                following.append(self.json_to_profile(user))

        self.log.debug('--Downloaded %i following' % len(following))
        return following

    def get_profile(self, user):
        self.log.debug('Getting profile of user %s' % user)
        rtn = self.request('/users/show', {'screen_name': user})
        profile = self.json_to_profile(rtn)
        self.log.debug('Getting recent statuses of user %s' % user)
        rtn = self.request('/statuses/user_timeline',
                           {'screen_name': user, 'count': 10})
        profile.recent_updates = self.json_to_status(rtn)
        return profile

    def get_blocked(self):
        return []

    def get_rate_limits(self):
        self.log.debug('Getting rate limits')
        rtn = self.request('/account/rate_limit_status')
        return self.json_to_ratelimit(rtn)

    def update_profile(self, p_args):
        self.log.debug('Updating profile')

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

        rtn = self.request('/account/update_profile', args)
        return self.json_to_profile(rtn)

    def update_status(self, text, in_reply_id=None):
        self.log.debug(u'Updating status: %s' % text)
        if in_reply_id:
            args = {'status': text, 'in_reply_to_status_id': in_reply_id}
        else:
            args = {'status': text}

        rtn = self.request('/statuses/update', args)
        return self.json_to_status(rtn)

    def destroy_status(self, status_id):
        self.log.debug('Destroying status: %s' % status_id)
        rtn = self.request('/statuses/destroy', {'id': status_id})
        return self.json_to_status(rtn)

    def send_direct(self, screen_name, text):
        self.log.debug('Sending direct to %s' % screen_name)
        args = {'screen_name': screen_name, 'text': text}
        rtn = self.request('/direct_messages/new', args)
        return self.json_to_status(rtn)

    def destroy_direct(self, id_):
        return None

    def repeat(self, status_id):
        self.log.debug('Repeating status %s' % status_id)
        rtn = self.request('/statuses/retweet', {'id': status_id})
        status = self.json_to_status(rtn)
        #status.reposted_by = self.__get_retweet_users(status_id)
        return status

    def mark_favorite(self, status_id):
        self.log.debug('Marking status %s as favorite' % status_id)
        rtn = self.request('/favorites/create', {'id': status_id})
        return self.json_to_status(rtn)

    def unmark_favorite(self, status_id):
        self.log.debug('Unmarking status %s as favorite' % status_id)
        rtn = self.request('/favorites/destroy', {'id': status_id})
        return self.json_to_status(rtn)

    def follow(self, screen_name, by_id=False):
        self.log.debug('Follow to %s' % screen_name)
        if by_id:
            arg = {'user_id': screen_name}
        else:
            arg = {'screen_name': screen_name}
        rtn = self.request('/friendships/create', arg)
        return self.json_to_profile(rtn)

    def unfollow(self, screen_name):
        self.log.debug('Unfollow to %s' % screen_name)
        rtn = self.request('/friendships/destroy',
                           {'screen_name': screen_name})
        return self.json_to_profile(rtn)

    def block(self, screen_name):
        self.log.debug('Blocking user %s' % screen_name)
        rtn = self.request('/blocks/create', {'screen_name': screen_name})
        return self.json_to_profile(rtn)

    def unblock(self, screen_name):
        self.log.debug('Unblocking user %s' % screen_name)
        rtn = self.request('/blocks/destroy', {'screen_name': screen_name})
        return self.json_to_profile(rtn)

    def search(self, query, count=STATUSPP):
        self.log.debug('Searching: %s' % query)
        rtn = self.request('/search', {'q': query, 'rpp': count},
                           base_url=self.urls['search'])
        return self.json_to_status(rtn['results'])

    def is_friend(self, user):
        self.log.debug('Testing friendship of %s against %s' % (self.uname, user))
        result = self.request('/friendships/show',
                              {'source_screen_name': self.uname,
                              'target_screen_name': user})
        return result['relationship']['target']['following']
        '''
        self.log.debug('Testing friendship with %s' % user)
        result = self.request('/friendships/exists',
                              {'screen_name_a': self.uname,
                              'screen_name_b': user},
                               format='xml')
        print result
        if result.find('true') > 0:
            return True
        elif result.find('false') > 0:
            return False '''

    def get_profile_image(self, user):
        self.log.debug('Getting profile image for %s' % (user))
        url = '/users/profile_image/%s' % user
        result = self.request(url,
                              {'screen_name': user, 'size': 'original'},
                              fmt='xml')
        #result = self.request('/users/profile_image',
        #    {'screen_name': user, 'size': 'original'}, fmt='xml')
        return result
