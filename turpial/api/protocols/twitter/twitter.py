# -*- coding: utf-8 -*-

""" Twitter implementation for Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 25, 2010

import urllib2

from turpial.api.common import UpdateType, STATUSPP
from turpial.api.models.status import Status
from turpial.api.models.profile import Profile
from turpial.api.models.ratelimit import RateLimit
from turpial.api.protocols.twitter import oauth
from turpial.api.interfaces.protocol import Protocol
from turpial.api.protocols.twitter.globals import CONSUMER_KEY, CONSUMER_SECRET

#TODO: Implement get_retweet_users

class Main(Protocol):
    def __init__(self, username, account_id):
        p_name = 'Twitter(%s)' % username
        Protocol.__init__(self, account_id, p_name, 
            'http://api.twitter.com/1', 
            'http://search.twitter.com', 
            'http://twitter.com/search?q=%23', 
            None, 
            'http://www.twitter.com')
        
        self.uname = None
        self.token = None
        self.account_id = account_id
        self.auth_args = {}
        self.access_url = 'https://api.twitter.com/oauth/access_token'
        
        self.consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
        self.sign_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
        
    def __fetch_xauth_access_token(self, username, password):
        request = oauth.OAuthRequest.from_consumer_and_token(
            oauth_consumer=self.consumer,
            http_method='POST', http_url=self.access_url,
            parameters = {
                'x_auth_mode': 'client_auth',
                'x_auth_username': username,
                'x_auth_password': password
            }
        )
        request.sign_request(self.sign_method_hmac_sha1, self.consumer, None)

        req = urllib2.Request(self.access_url, data=request.to_postdata())
        response = urllib2.urlopen(req)
        self.token = oauth.OAuthToken.from_string(response.read())
        self.auth_args['key'] = self.token.key
        self.auth_args['secret'] = self.token.secret
        
    def auth_http_request(self, httpreq, args):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
            token=self.token, http_method=httpreq.method, http_url=httpreq.uri,
            parameters=httpreq.params)
        request.sign_request(self.sign_method_hmac_sha1,
            self.consumer, self.token)
        httpreq.headers.update(request.to_header())
        return httpreq
        
    def json_to_profile(self, response):
        if isinstance(response, list):
            profiles = []
            for pf in response:
                profile = self.json_to_profile(pf)
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
                if status.retweet_by:
                    users = self.get_retweet_users(status._id)
                    status.retweet_by = users
                statuses.append(status)
            return statuses
        else:
            retweet_by = None
            if response.has_key('retweeted_status'):
                retweet_by = response['user']['screen_name']
                tweet = response['retweeted_status']
            else:
                tweet = response
            
            if tweet.has_key('user'):
                username = tweet['user']['screen_name']
                avatar = tweet['user']['profile_image_url']
            elif tweet.has_key('sender'):
                username = tweet['sender']['screen_name']
                avatar = tweet['sender']['profile_image_url']
            elif tweet.has_key('from_user'):
                username = tweet['from_user']
                avatar = tweet['profile_image_url']
            
            in_reply_to_id = None
            in_reply_to_user = None
            if tweet.has_key('in_reply_to_status_id') and \
               tweet['in_reply_to_status_id']:
                in_reply_to_id = tweet['in_reply_to_status_id']
                in_reply_to_user = tweet['in_reply_to_screen_name']
                
            fav = False
            if tweet.has_key('favorited'):
                fav = tweet['favorited']
            
            source = None
            if tweet.has_key('source'):
                source = tweet['source']
            
            own = True if (username.lower() == self.uname.lower()) else False
            
            status = Status()
            status.id_ = str(tweet['id'])
            status.username = username
            status.avatar = avatar
            status.source = source
            status.text = tweet['text']
            status.in_reply_to_id = in_reply_to_id
            status.in_reply_to_user = in_reply_to_user
            status.is_favorite = fav
            status.reposted_by = retweet_by
            status.datetime = self.get_str_time(tweet['created_at'])
            status.timestamp = self.get_int_time(tweet['created_at'])
            status._type = _type
            status.account_id = self.account_id
            status.is_own = own
            return status
            
    def json_to_ratelimit(self, response):
        rate = RateLimit()
        rate.hourly_limit = response['hourly_limit']
        rate.remaining_hits = response['remaining_hits']
        rate.reset_time = response['reset_time']
        rate.reset_time_in_seconds = response['reset_time_in_seconds']
        return rate
        
    def auth(self, username, password):
        self.log.debug('Starting OAuth')
        
        self.__fetch_xauth_access_token(username, password)
        rtn = self.request('/account/verify_credentials')
        profile = self.json_to_profile(rtn)
        self.uname = profile.username
        return profile
        
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
        
    def get_lists(self):
        self.log.debug('Getting user lists')
        tries = 0
        count = 0
        cursor = -1
        lists = []
        
        # Downloading own lists
        while 1:
            try:
                rtn = self.request('/%s/lists' % self.uname, {'cursor': cursor})
            except Exception, exc:
                tries += 1
                if tries < 3:
                    continue
                else:
                    raise Exception
                
            for ls in rtn['lists']:
                lists.append(self.json_to_list(ls))
                count += 1
            if rtn['next_cursor'] > 0:
                cursor = rtn['next_cursor']
                continue
            else:
                break
        
        # Downloading suscribed lists
        while 1:
            try:
                rtn = self.request('/%s/lists/subscriptions' % self.uname, 
                    {'cursor': cursor})
            except Exception, exc:
                tries += 1
                if tries < 3:
                    continue
                else:
                    raise Exception
                
            for ls in rtn['lists']:
                lists.append(self.json_to_list(ls))
                count += 1
            if rtn['next_cursor'] > 0:
                cursor = rtn['next_cursor']
                continue
            else:
                break
        
        self.log.debug('--Downloaded %i lists' % count)
        return lists
        
    def get_list_statuses(self, list_id, user, count=STATUSPP):
        self.log.debug('Getting list %s statuses' % list_id)
        rtn = self.request('/%s/lists/%s/statuses' % (user, list_id), 
            {'per_page': count})
        return self.json_to_status(rtn)
        
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
                
            for user in rtn['users']:
                friends.append(self.json_to_profile(user))
                count += 1
            
            if rtn['next_cursor'] > 0:
                cursor = rtn['next_cursor']
            else:
                break
        
        self.log.debug('--Downloaded %i friends' % count)
        return friends
        
    def get_rate_limits(self):
        self.log.debug('Getting rate limits')
        rtn = self.request('/account/rate_limit_status')
        return self.json_to_ratelimit(rtn)
        
    def get_retweet_users(self, status_id):
        self.log.debug('Getting users of a retweet')
        users = []
        rtn = self.request('/statuses/%s/retweeted_by' % status_id)
        for item in rtn:
            profile = self.json_to_profile(item)
            users.append(profile.username)
        return users
        
    def update_profile(self, name='', url='', bio='', location=''):
        self.log.debug('Updating profile')
        
        args = {'name': name, 'url': url, 'description': bio, 
            'location': location}
        rtn = self.request('/account/update_profile', args)
        return self.json_to_profile(rtn)
    
    def update_status(self, text, in_reply_id=None):
        self.log.debug('Updating status: %s' % text)
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
        
    def destroy_direct(self, status_id):
        self.log.debug('Destroying direct %s' % status_id)
        rtn = self.request('/direct_messages/destroy', {'id': status_id})
        return self.json_to_status(rtn)
        
    def repost(self, status_id):
        self.log.debug('Retweeting status %s' % status_id)
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
