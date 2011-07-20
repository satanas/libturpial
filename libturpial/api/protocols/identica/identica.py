# -*- coding: utf-8 -*-

""" Identi.ca implementation for Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Jun 08, 2010

import re

from libturpial.common import UpdateType, STATUSPP
from libturpial.api.models.status import Status
from libturpial.api.models.profile import Profile
from libturpial.api.interfaces.protocol import Protocol

class Main(Protocol):
    GROUP_PATTERN = re.compile('(?<![\w])![\wáéíóúÁÉÍÓÚñÑçÇ]+')
    
    def __init__(self, username, account_id):
        p_name = 'Identi.ca(%s)' % username
        Protocol.__init__(self, account_id, p_name, 
            'http://identi.ca/api', 
            'http://identi.ca/api', 
            'http://identi.ca/tag/', 
            'http://identi.ca/group',
            'http://identi.ca')
        
        self.uname = None
        self.account_id = account_id
    
    def json_to_profile(self, response):
        if isinstance(response, list):
            profiles = []
            for pf in response:
                profile = self.json_to_status(json_to_profile)
                profiles.append(profile)
            return profiles
        else:
            profile = Profile()
            profile.id_ = response['id']
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
            if response.has_key('status'):
                profile.last_update = response['status']['text']
                profile.last_update_id = response['status']['id']
            profile.link_color = ('#' + response['profile_link_color']) or Profile.DEFAULT_LINK_COLOR
            return profile
    
    def json_to_status(self, response, _type=UpdateType.STD):
        if isinstance(response, list):
            statuses = []
            for resp in response:
                if not resp:
                    continue
                status = self.json_to_status(resp, _type)
                statuses.append(status)
            return statuses
        else:
            retweet_by = None
            if response.has_key('retweeted_status'):
                retweet_by = response['user']['screen_name']
                dent = response['retweeted_status']
            else:
                dent = response
            
            if dent.has_key('user'):
                username = dent['user']['screen_name']
                avatar = dent['user']['profile_image_url']
            elif dent.has_key('sender'):
                username = dent['sender']['screen_name']
                avatar = dent['sender']['profile_image_url']
            elif dent.has_key('from_user'):
                username = dent['from_user']
                avatar = dent['profile_image_url']
            
            in_reply_to_id = None
            in_reply_to_user = None
            if dent.has_key('in_reply_to_status_id') and \
               dent['in_reply_to_status_id']:
                in_reply_to_id = dent['in_reply_to_status_id']
                in_reply_to_user = dent['in_reply_to_screen_name']
                
            fav = False
            if dent.has_key('favorited'):
                fav = dent['favorited']
            
            source = None
            if dent.has_key('source'):
                source = dent['source']
            
            own = True if (username.lower() == self.uname.lower()) else False
            
            status = Status()
            status.id_ = str(dent['id'])
            status.username = username
            status.avatar = avatar
            status.source = self.get_source(source)
            status.text = dent['text']
            status.in_reply_to_id = in_reply_to_id
            status.in_reply_to_user = in_reply_to_user
            status.is_favorite = fav
            status.reposted_by = retweet_by
            status.datetime = self.get_str_time(dent['created_at'])
            status.timestamp = self.get_int_time(dent['created_at'])
            status.entities = self.get_entities(dent)
            status._type = _type
            status.account_id = self.account_id
            status.is_own = own
            return status
    
    def auth(self, username, password):
        ''' Start Auth '''
        self.log.debug('Starting Basic Auth')
        self.auth_args = {'username': username, 'password': password}
        rtn = self.request('/account/verify_credentials')
        profile = self.json_to_profile(rtn)
        self.uname = profile.username
        return profile
        
    def get_entities(self, status):
        entities = Protocol.get_entities(self, status)
        groups = []
        for item in self.GROUP_PATTERN.findall(status['text']):
            groups.append(item)
        entities['groups'] = groups
        return entities
        
    def get_timeline(self, count=STATUSPP):
        self.log.debug('Getting timeline')
        rtn = self.request('/statuses/home_timeline', {'count': count})
        return self.json_to_status(rtn)
        
    def get_replies(self, count=STATUSPP):
        self.log.debug('Getting replies')
        rtn = self.request('/statuses/mentions', {'count': count})
        return self.json_to_status(rtn)
        
    def get_directs(self, count=STATUSPP):
        self.log.debug('Getting directs')
        rtn = self.request('/direct_messages', {'count': count / 2})
        directs = self.json_to_status(rtn, _type=UpdateType.DM)
        rtn2 = self.request('/direct_messages/sent', {'count': count / 2})
        directs += self.json_to_status(rtn2, _type=UpdateType.DM)
        return directs
            
    def get_sent(self, count=STATUSPP):
        self.log.debug('Getting my statuses')
        rtn = self.request('/statuses/user_timeline', {'count': count})
        return self.json_to_status(rtn)
        
    def get_favorites(self):
        self.log.debug('Getting favorites')
        rtn = self.request('/favorites')
        return self.json_to_status(rtn)
        
    def get_lists(self, username):
        return []
        
    def get_list_statuses(self, list_id, user, count=STATUSPP):
        pass
    
    def get_conversation(self, status_id):
        self.log.debug('Getting conversation')
        conversation = []
        
        while 1:
            rtn = self.request('/statuses/show', {'id': status_id})
            self.log.debug('--Fetched status: %s' % status_id)
            conversation.append(self.json_to_status(rtn))
            
            if rtn['in_reply_to_status_id']:
                status_id = str(rtn['in_reply_to_status_id'])
            else:
                break
        return conversation
        
    def get_friends(self):
        self.log.debug('Getting friends list')
        tries = 0
        count = 0
        cursor = -1
        friends = []
        
        while 1:
            try:
                rtn = self.request('/statuses/friends', {'cursor': cursor})
            except Exception, exc:
                tries += 1
                if tries < 3:
                    continue
                else:
                    raise Exception
                
            for user in rtn:
                friends.append(self.json_to_profile(user))
                count += 1
            break
            '''
            if rtn['next_cursor'] > 0:
                cursor = rtn['next_cursor']
            else:
                break
            '''
        self.log.debug('--Downloaded %i friends' % count)
        return friends
        
    def get_profile(self, user):
        self.log.debug('Getting profile of user %s' % user)
        rtn = self.request('/users/show', {'screen_name': user})
        return self.json_to_profile(rtn)
    
    def get_rate_limits(self):
        self.log.debug('Getting rate limits')
        rtn = self.request('/account/rate_limit_status')
        return self.json_to_ratelimit(rtn)
        
    def update_profile(self, p_args):
        self.log.debug('Updating profile')
        
        # We use if's instead update method to guarantee valid arguments
        args = {}
        if p_args.has_key('name'):
            args['name'] = p_args['name']
        if p_args.has_key('url'):
            args['url'] = p_args['url']
        if p_args.has_key('description'):
            args['description'] = p_args['description']
        if p_args.has_key('location'):
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
        
    def repost(self, status_id):
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
        
    def follow(self, screen_name):
        self.log.debug('Follow to %s' % screen_name)
        rtn = self.request('/friendships/create', {'screen_name': screen_name})
        return self.json_to_profile(rtn)
        
    def unfollow(self, screen_name):
        self.log.debug('Unfollow to %s' % screen_name)
        rtn = self.request('/friendships/destroy', {'screen_name': screen_name})
        return self.json_to_profile(rtn)
        
    def search(self, query, count=STATUSPP):
        self.log.debug('Searching: %s' % query)
        rtn = self.request('/search',{'q': query, 'rpp': count}, 
            base_url=self.urls['search'])
        return self.json_to_status(rtn['results'])
