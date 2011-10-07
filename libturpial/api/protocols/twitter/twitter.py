# -*- coding: utf-8 -*-

""" Twitter implementation for Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 25, 2010

import base64
import urllib2
import traceback

from libturpial.common import UpdateType, STATUSPP
from libturpial.api.models.list import List
from libturpial.api.models.status import Status
from libturpial.api.models.profile import Profile
from libturpial.api.models.ratelimit import RateLimit
from libturpial.api.interfaces.protocol import Protocol
from libturpial.api.models.trend import Trend, TrendsResults
from libturpial.api.protocols.twitter.globals import CK, CS, SALT

class Main(Protocol):
    def __init__(self, username, account_id, auth):
        p_name = 'Twitter(%s)' % username
        Protocol.__init__(self, account_id, p_name, 
            'http://api.twitter.com/1', 
            'http://search.twitter.com', 
            'http://twitter.com/search?q=%23', 
            None, 
            'http://www.twitter.com')
        
        self.REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
        self.ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
        self.AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
        
        self.uname = None
        self.account_id = account_id
        self.set_consumer(CK, base64.b64decode(CS + SALT))
        if auth:
            self.set_auth_info(auth)
    
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
            profile.protected = response['protected']
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
                if status.reposted_by:
                    users = self.get_retweet_users(status.id_)
                    status.reposted_by = users
                statuses.append(status)
            return statuses
        else:
            reposted_by = None
            if response.has_key('retweeted_status'):
                reposted_by = response['user']['screen_name']
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
            status.source = self.get_source(source)
            status.text = tweet['text']
            status.in_reply_to_id = in_reply_to_id
            status.in_reply_to_user = in_reply_to_user
            status.is_favorite = fav
            status.reposted_by = reposted_by
            status.datetime = self.get_str_time(tweet['created_at'])
            status.timestamp = self.get_int_time(tweet['created_at'])
            status.entities = self.get_entities(tweet)
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
        
    def json_to_list(self, response):
        if isinstance(response, list):
            lists = []
            for li in response:
                _list = self.json_to_list(li)
                lists.append(_list)
            return lists
        else:
            _list = List()
            _list.id_ = str(response['id'])
            _list.user = response['user']
            _list.name = response['slug']
            _list.title = response['name']
            _list.suscribers = response['subscriber_count']
            _list.description = response['description']
            _list.single_unit = 'tweet'
            _list.plural_unit = 'tweets'
            return _list
    
    def json_to_trend(self, response):
        if isinstance(response, list):
            trends = []
            for tr in response:
                trend = self.json_to_trend(tr)
                trends.append(trend)
            return trends
        else:
            trend = Trend()
            trend.name = response['name']
            trend.promoted = False
            if response['promoted_content']:
                trend.promoted = True
            return trend
    
    def auth(self, username, password):
        self.log.debug('Starting OAuth')
        
        rtn = self.request('/account/verify_credentials')
        profile = self.json_to_profile(rtn)
        self.uname = profile.username
        return profile
        
    def get_entities(self, tweet):
        if tweet.has_key('entities'):
            entities = {}
            mentions = []
            for mention in tweet['entities']['user_mentions']:
                mentions.append('@'+mention['screen_name'])
            entities['mentions'] = mentions
            
            urls = []
            for url in tweet['entities']['urls']:
                urls.append(url['url'])
            entities['url'] = urls
            
            hashtags = []
            for ht in tweet['entities']['hashtags']:
                hashtags.append('#'+ht['text'])
            entities['hashtags'] = hashtags
        else:
            entities = Protocol.get_entities(self, tweet)
        return entities
        
    def get_timeline(self, count=STATUSPP):
        self.log.debug('Getting timeline')
        rtn = self.request('/statuses/home_timeline', {'count': count, 
            'include_entities': True})
        return self.json_to_status(rtn)
        
    def get_replies(self, count=STATUSPP):
        self.log.debug('Getting replies')
        rtn = self.request('/statuses/mentions', {'count': count,
            'include_entities': True})
        return self.json_to_status(rtn)
        
    def get_directs(self, count=STATUSPP):
        self.log.debug('Getting directs')
        rtn = self.request('/direct_messages', {'count': count / 2, 
            'include_entities': True})
        directs = self.json_to_status(rtn, _type=UpdateType.DM)
        rtn2 = self.request('/direct_messages/sent', {'count': count / 2,
        'include_entities': True})
        directs += self.json_to_status(rtn2, _type=UpdateType.DM)
        return directs
            
    def get_sent(self, count=STATUSPP):
        self.log.debug('Getting my statuses')
        rtn = self.request('/statuses/user_timeline', {'count': count,
            'include_entities': True})
        return self.json_to_status(rtn)
        
    def get_favorites(self, count=STATUSPP):
        self.log.debug('Getting favorites')
        rtn = self.request('/favorites', {'include_entities': True})
        return self.json_to_status(rtn)
        
    def get_public_timeline(self, count=STATUSPP):
        self.log.debug('Getting public timeline')
        rtn = self.request('/statuses/public_timeline', {'count': count, 
            'include_entities': True})
        return self.json_to_status(rtn)
        
    def get_lists(self, username):
        self.log.debug('Getting user lists')
        rtn = self.request('/lists/all', {'screen_name': username})
        lists = self.json_to_list(rtn)
        self.log.debug('--Downloaded %i lists' % len(lists))
        return lists
        
    def get_list_statuses(self, list_id, count=STATUSPP):
        self.log.debug('Getting statuses from list %s' % list_id)
        rtn = self.request('/lists/statuses', {'list_id': list_id, 
            'per_page': count, 'include_entities': True})
        return self.json_to_status(rtn)
        
    def get_conversation(self, status_id):
        self.log.debug('Getting conversation for status %s' % status_id)
        conversation = []
        
        while 1:
            rtn = self.request('/statuses/show', {'id': status_id,
                'include_entities': True})
            self.log.debug('--Fetched status: %s' % status_id)
            conversation.append(self.json_to_status(rtn))
            
            if rtn['in_reply_to_status_id']:
                status_id = str(rtn['in_reply_to_status_id'])
            else:
                break
        return conversation
        
    def get_friends(self):
        self.log.debug('Getting friends list')
        count = 0
        cursor = -1
        current = 0
        max_friends_req = 100
        
        friends = []
        while 1:
            # Fetch user_ids (up to 5000 for each request)
            rtn = self.request('/friends/ids', {'cursor': cursor})
            total = len(rtn['ids'])
            if total == 0:
                return friends
            while 1:
                if current + max_friends_req <= total:
                    batch = rtn['ids'][current:current + max_friends_req]
                    current += max_friends_req
                else:
                    batch = rtn['ids'][current:total]
                    current = total
                
                # Fetch user details (up to 100 for each request)
                user_ids = ','.join([str(x) for x in batch])
                rtn2 = self.request('/users/lookup', {'user_id': user_ids})
                for user in rtn2:
                    friends.append(self.json_to_profile(user))
                    count += 1
                if current == total:
                    break
            
            if rtn['next_cursor'] > 0:
                cursor = rtn['next_cursor']
            else:
                break
        
        self.log.debug('--Downloaded %i friends' % count)
        return friends
        
    def get_profile(self, user):
        self.log.debug('Getting profile of user %s' % user)
        rtn = self.request('/users/show', {'screen_name': user})
        return self.json_to_profile(rtn)
        
    def get_blocked(self):
        self.log.debug('Getting list of blocked users')
        rtn = self.request('/blocks/blocking')
        return self.json_to_profile(rtn)
        
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
        self.log.debug('Updating status: %s' % text)
        if in_reply_id:
            args = {'status': text, 'in_reply_to_status_id': in_reply_id}
        else:
            args = {'status': text}
        args['include_entities'] = True
        rtn = self.request('/statuses/update', args)
        return self.json_to_status(rtn)
        
    def destroy_status(self, status_id):
        self.log.debug('Destroying status: %s' % status_id)
        rtn = self.request('/statuses/destroy', {'id': status_id,
            'include_entities': True})
        return self.json_to_status(rtn)
        
    def send_direct(self, screen_name, text):
        self.log.debug('Sending direct to %s' % screen_name)
        args = {'screen_name': screen_name, 'text': text, 
            'include_entities': True}
        rtn = self.request('/direct_messages/new', args)
        return self.json_to_status(rtn)
        
    def destroy_direct(self, status_id):
        self.log.debug('Destroying direct %s' % status_id)
        rtn = self.request('/direct_messages/destroy', {'id': status_id,
            'include_entities': True})
        return self.json_to_status(rtn)
        
    def repeat(self, status_id):
        self.log.debug('Retweeting status %s' % status_id)
        rtn = self.request('/statuses/retweet', {'id': status_id})
        status = self.json_to_status(rtn)
        status.reposted_by = self.get_retweet_users(status_id)
        return status
    
    def mark_favorite(self, status_id):
        self.log.debug('Marking status %s as favorite' % status_id)
        rtn = self.request('/favorites/create', {'id': status_id,
            'include_entities': True})
        return self.json_to_status(rtn)
        
    def unmark_favorite(self, status_id):
        self.log.debug('Unmarking status %s as favorite' % status_id)
        rtn = self.request('/favorites/destroy', {'id': status_id,
            'include_entities': True})
        return self.json_to_status(rtn)
        
    def follow(self, screen_name):
        self.log.debug('Follow to %s' % screen_name)
        rtn = self.request('/friendships/create', {'screen_name': screen_name})
        return self.json_to_profile(rtn)
        
    def unfollow(self, screen_name):
        self.log.debug('Unfollow to %s' % screen_name)
        rtn = self.request('/friendships/destroy', {'screen_name': screen_name})
        return self.json_to_profile(rtn)
        
    def block(self, screen_name):
        self.log.debug('Blocking user %s' % screen_name)
        rtn = self.request('/blocks/create', {'screen_name': screen_name})
        return self.json_to_profile(rtn)
        
    def unblock(self, screen_name):
        self.log.debug('Unblocking user %s' % screen_name)
        rtn = self.request('/blocks/destroy', {'screen_name': screen_name})
        return self.json_to_profile(rtn)
        
    def report_spam(self, screen_name):
        self.log.debug('Reporting user %s as spammer' % screen_name)
        rtn = self.request('/report_spam', {'screen_name': screen_name})
        return self.json_to_profile(rtn)
        
    def search(self, query, count=STATUSPP):
        self.log.debug('Searching: %s' % query)
        rtn = self.request('/search',{'q': query, 'rpp': count}, 
            base_url=self.urls['search'])
        return self.json_to_status(rtn['results'])
        
    def trends(self):
        self.log.debug('Searching for current trends')
        rtn = self.request('/trends/current')
        results = rtn['trends'].popitem()
        current = TrendsResults()
        current.title = 'Current Trends'
        current.timestamp = results[0]
        current.items = self.json_to_trend(results[1])
        
        rtn = self.request('/trends/daily')
        results = rtn['trends'].popitem()
        daily = TrendsResults()
        daily.title = 'Daily Trends'
        daily.timestamp = results[0]
        daily.items = self.json_to_trend(results[1])
        
        rtn = self.request('/trends/weekly')
        results = rtn['trends'].popitem()
        weekly = TrendsResults()
        weekly.title = 'Weekly Trends'
        weekly.timestamp = results[0]
        weekly.items = self.json_to_trend(results[1])
        return [current, daily, weekly]
    
    def is_friend(self, user):
        self.log.debug('Testing friendship of %s against %s' % (self.uname, user))
        result = self.request('/friendships/show', 
            {'source_screen_name': self.uname, 'target_screen_name': user})
        return result['relationship']['target']['following']
