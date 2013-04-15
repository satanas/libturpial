# -*- coding: utf-8 -*-

""" Twitter implementation for Turpial"""

from libturpial.api.models.list import List
from libturpial.api.models.status import Status
from libturpial.api.models.entity import Entity
from libturpial.api.models.profile import Profile
from libturpial.api.models.ratelimit import RateLimit
from libturpial.api.interfaces.protocol import Protocol
from libturpial.api.interfaces.http import TurpialHTTPOAuth
from libturpial.api.models.trend import Trend, TrendsResults
from libturpial.api.protocols.twitter.params import OAUTH_OPTIONS
from libturpial.common import NUM_STATUSES, StatusType, StatusColumn

# TODO:
# * Use trim_user wherever we can to improve performance
# * Implement trends

class Main(Protocol):
    """Twitter implementation for libturpial"""
    def __init__(self):
        self.uname = None
        self.base_url = 'http://api.twitter.com/1.1'
        self.search_url = 'http://search.twitter.com'
        self.hashtags_url = 'http://twitter.com/search?q=%23'
        self.profiles_url = 'http://www.twitter.com'

        Protocol.__init__(self)

    def __build_basic_args(self, count, since_id):
        args = {'count': count, 'include_entities': True}
        if since_id:
            args['since_id'] = since_id
        return args

    def initialize_http(self):
        self.http = TurpialHTTPOAuth(self.base_url, OAUTH_OPTIONS)

    def setup_user_account(self, account_id, key, secret, verifier):
        self.account_id = account_id
        self.http.set_token_info(key, secret, verifier)
        self.uname = account_id.split('-')[0]


    #################################################################
    # Methods related to Twitter service
    #################################################################

    def verify_credentials(self):
        rtn = self.http.get('/account/verify_credentials', secure=True)
        profile = self.json_to_profile(rtn)
        self.uname = profile.username
        return profile

    def get_timeline(self, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        rtn = self.http.get('/statuses/home_timeline', args)
        return self.json_to_status(rtn, StatusColumn.TIMELINE)

    def get_replies(self, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        rtn = self.http.get('/statuses/mentions_timeline', args)
        return self.json_to_status(rtn, StatusColumn.REPLIES)

    def get_directs(self, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        rtn = self.http.get('/direct_messages', args)
        return self.json_to_status(rtn, StatusColumn.DIRECTS,
                                   _type=StatusType.DIRECT)

    def get_directs_sent(self, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        rtn = self.http.get('/direct_messages/sent', args)
        return self.json_to_status(rtn, StatusColumn.DIRECTS,
                                   _type=StatusType.DIRECT)

    def get_sent(self, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        args['include_rts'] = True
        rtn = self.http.get('/statuses/user_timeline', args)
        return self.json_to_status(rtn, StatusColumn.SENT)

    def get_favorites(self, count=NUM_STATUSES):
        rtn = self.http.get('/favorites/list', {'include_entities': True})
        return self.json_to_status(rtn, StatusColumn.FAVORITES)

    def get_public_timeline(self, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        rtn = self.http.get('/statuses/firehose', args)
        return self.json_to_status(rtn, StatusColumn.PUBLIC)

    def get_lists(self, username):
        rtn = self.http.get('/lists/list', {'screen_name': username})
        lists = self.json_to_list(rtn)
        self.log.debug('--Downloaded %i lists' % len(lists))
        return lists

    def get_list_statuses(self, list_id, count=NUM_STATUSES, since_id=None):
        args = {'list_id': list_id, 'per_page': count,
                'include_entities': True}
        if since_id:
            args['since_id'] = since_id
        rtn = self.http.get('/lists/statuses', args)
        return self.json_to_status(rtn, list_id)

    def get_conversation(self, status_id):
        conversation = []

        while 1:
            rtn = self.http.get('/statuses/show', {'id': status_id,
                               'include_entities': True})
            self.log.debug('--Fetched status: %s' % status_id)
            conversation.append(self.json_to_status(rtn,
                                StatusColumn.CONVERSATION))

            if rtn['in_reply_to_status_id']:
                status_id = str(rtn['in_reply_to_status_id'])
            else:
                break
        return conversation

    def get_status(self, status_id):
        rtn = self.http.get('/statuses/show', {'id': status_id,
                           'include_entities': True})
        return self.json_to_status(rtn)

    def get_followers(self, only_id=False):
        cursor = -1
        current = 0
        max_friends_req = 100
        followers = []

        while 1:
            # Fetch user_ids (up to 5000 for each request)
            rtn = self.http.get('/followers/ids', {'cursor': cursor})
            total = len(rtn['ids'])
            if total == 0:
                break

            if only_id:
                for id_ in rtn['ids']:
                    followers.append(str(id_))
            else:
                while 1:
                    if current + max_friends_req <= total:
                        batch = rtn['ids'][current:current + max_friends_req]
                        current += max_friends_req
                    else:
                        batch = rtn['ids'][current:total]
                        current = total

                    # Fetch user details (up to 100 for each request)
                    user_ids = ','.join([str(x) for x in batch])
                    rtn2 = self.http.get('/users/lookup', {'user_id': user_ids})
                    for user in rtn2:
                        followers.append(self.json_to_profile(user))
                    if current == total:
                        break

            if rtn['next_cursor'] > 0:
                cursor = rtn['next_cursor']
            else:
                break

        self.log.debug('--Downloaded %i followers' % len(followers))
        return followers

    def get_following(self, only_id=False):
        cursor = -1
        current = 0
        max_friends_req = 100
        following = []

        while 1:
            # Fetch user_ids (up to 5000 for each request)
            rtn = self.http.get('/friends/ids', {'cursor': cursor})
            total = len(rtn['ids'])
            if total == 0:
                break

            if only_id:
                for id_ in rtn['ids']:
                    following.append(str(id_))
            else:
                while 1:
                    if current + max_friends_req <= total:
                        batch = rtn['ids'][current:current + max_friends_req]
                        current += max_friends_req
                    else:
                        batch = rtn['ids'][current:total]
                        current = total

                    # Fetch user details (up to 100 for each request)
                    user_ids = ','.join([str(x) for x in batch])
                    rtn2 = self.http.get('/users/lookup', {'user_id': user_ids})
                    for user in rtn2:
                        following.append(self.json_to_profile(user))
                    if current == total:
                        break

            if rtn['next_cursor'] > 0:
                cursor = rtn['next_cursor']
            else:
                break

        self.log.debug('--Downloaded %i following' % len(following))
        return following

    def get_profile(self, user):
        rtn = self.http.get('/users/show', {'screen_name': user})
        profile = self.json_to_profile(rtn)
        rtn = self.http.get('/statuses/user_timeline',
                           {'screen_name': user, 'count': 10,
                           'include_entities': True})
        profile.recent_updates = self.json_to_status(rtn)
        return profile

    def get_blocked(self):
        rtn = self.http.get('/blocks/list')
        return self.json_to_profile(rtn['users'])
    #
    #def get_rate_limits(self):
    #    rtn = self.http.get('/account/rate_limit_status')
    #    print rtn
    #    return self.json_to_ratelimit(rtn)

    def get_repeaters(self, status_id, only_username=False):
        users = []
        rtn = self.http.get('/statuses/retweets/%s' % status_id)
        for item in rtn:
            if only_username:
                users.append(item['user']['screen_name'])
            else:
                profile = self.json_to_profile(item['user'])
                users.append(profile)
        return users

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

        rtn = self.http.post('/account/update_profile', args)
        return self.json_to_profile(rtn)

    def update_status(self, text, in_reply_id=None):
        if in_reply_id:
            args = {'status': text, 'in_reply_to_status_id': in_reply_id}
        else:
            args = {'status': text}
        args['include_entities'] = True
        rtn = self.http.post('/statuses/update', args)
        return self.json_to_status(rtn)

    def destroy_status(self, status_id):
        rtn = self.http.post('/statuses/destroy', {'id': status_id,
                           'include_entities': True})
        return self.json_to_status(rtn)

    def repeat_status(self, status_id):
        rtn = self.http.post('/statuses/retweet', {'id': status_id})
        status = self.json_to_status(rtn)
        status.reposted_by = self.get_repeaters(status_id)
        return status

    def mark_as_favorite(self, status_id):
        rtn = self.http.post('/favorites/create', {'id': status_id,
                           'include_entities': True}, id_in_url=False)
        return self.json_to_status(rtn)

    def unmark_as_favorite(self, status_id):
        rtn = self.http.post('/favorites/destroy', {'id': status_id,
                           'include_entities': True}, id_in_url=False)
        return self.json_to_status(rtn)

    def follow(self, screen_name, by_id=False):
        if by_id:
            arg = {'user_id': screen_name}
        else:
            arg = {'screen_name': screen_name}
        rtn = self.http.post('/friendships/create', arg)
        return self.json_to_profile(rtn)

    def unfollow(self, screen_name):
        rtn = self.http.post('/friendships/destroy',
                           {'screen_name': screen_name})
        return self.json_to_profile(rtn)

    def send_direct_message(self, screen_name, text):
        args = {'screen_name': screen_name, 'text': text,
                'include_entities': True}
        rtn = self.http.post('/direct_messages/new', args)
        return self.json_to_status(rtn)

    def destroy_direct_message(self, direct_message_id):
        rtn = self.http.post('/direct_messages/destroy', {'id': direct_message_id,
                           'include_entities': True})
        return self.json_to_status(rtn)

    def block(self, screen_name):
        rtn = self.http.post('/blocks/create', {'screen_name': screen_name})
        return self.json_to_profile(rtn)

    def unblock(self, screen_name):
        rtn = self.http.post('/blocks/destroy', {'screen_name': screen_name})
        return self.json_to_profile(rtn)

    def report_as_spam(self, screen_name):
        rtn = self.http.post('/users/report_spam', {'screen_name': screen_name})
        return self.json_to_profile(rtn)

    def search(self, query, count=NUM_STATUSES, since_id=None):
        args = self.__build_basic_args(count, since_id)
        args['q'] = query
        rtn = self.http.get('/search', args, base_url=self.search_url)
        return self.json_to_status(rtn['results'])

    #def trends(self):
    #    rtn = self.http.get('/trends/current')
    #    results = rtn['trends'].popitem()
    #    current = TrendsResults()
    #    current.title = 'Current Trends'
    #    current.timestamp = results[0]
    #    current.items = self.json_to_trend(results[1])

    #    rtn = self.http.get('/trends/daily')
    #    results = rtn['trends'].popitem()
    #    daily = TrendsResults()
    #    daily.title = 'Daily Trends'
    #    daily.timestamp = results[0]
    #    daily.items = self.json_to_trend(results[1])

    #    rtn = self.http.get('/trends/weekly')
    #    results = rtn['trends'].popitem()
    #    weekly = TrendsResults()
    #    weekly.title = 'Weekly Trends'
    #    weekly.timestamp = results[0]
    #    weekly.items = self.json_to_trend(results[1])
    #    return [current, daily, weekly]

    def is_friend(self, user):
        result = self.http.get('/friendships/show',
                              {'source_screen_name': self.uname,
                              'target_screen_name': user})
        return result['relationship']['target']['following']

    def get_profile_image(self, user):
        rtn = self.http.get('/users/show', {'screen_name': user})
        return rtn['profile_image_url'].replace('_normal', '')

    #################################################################
    # Methods to convert JSON responses into objects
    #################################################################

    # TODO: Try to do this with metaprogramming (a single JSON object that
    # knows how to become a turpial object

    def json_to_profile(self, response):

        if isinstance(response, list):
            profiles = []
            for pf in response:
                profile = self.json_to_profile(pf)
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
            profile.follow_request = response['follow_request_sent']
            profile.favorites_count = response['favourites_count']
            profile.protected = response['protected']
            profile.verified = response['verified']
            if 'status' in response:
                profile.last_update = response['status']['text']
                profile.last_update_id = response['status']['id']
            profile.link_color = ('#' + response['profile_link_color']) or Profile.DEFAULT_LINK_COLOR
            return profile

    def json_to_status(self, response, column_id='', _type=StatusType.NORMAL):
        if isinstance(response, list):
            statuses = []
            for resp in response:
                if not resp:
                    continue
                status = self.json_to_status(resp, column_id, _type)
                if status.reposted_by:
                    # TODO: Handle this
                    #users = self.get_retweet_users(status.id_)
                    #status.reposted_by = users
                    #count = self.get_retweet_count(status.id_)
                    #status.reposted_count = count
                    pass
                statuses.append(status)
            return statuses
        else:
            reposted_by = None
            retweeted_id = None
            if 'retweeted_status' in response:
                reposted_by = response['user']['screen_name']
                retweeted_id = response['id']
                post = response['retweeted_status']
            else:
                post = response

            protected = False
            verified = False
            if 'user' in post:
                username = post['user']['screen_name']
                avatar = post['user']['profile_image_url']
                protected = post['user']['protected']
                verified = post['user']['verified']
            elif 'sender' in post:
                username = post['sender']['screen_name']
                avatar = post['sender']['profile_image_url']
                protected = post['sender']['protected']
                verified = post['sender']['verified']
            elif 'from_user' in post:
                username = post['from_user']
                avatar = post['profile_image_url']

            in_reply_to_id = None
            in_reply_to_user = None
            if 'in_reply_to_status_id' in post and post['in_reply_to_status_id']:
                in_reply_to_id = post['in_reply_to_status_id']
                if 'in_reply_to_screen_name' in post:
                    in_reply_to_user = post['in_reply_to_screen_name']

            fav = False
            if 'favorited' in post:
                fav = post['favorited']

            retweeted = False
            if 'retweeted' in post:
                retweeted = post['retweeted']

            source = None
            if 'source' in post:
                source = post['source']

            status = Status()
            status.id_ = str(post['id'])
            status.retweeted_id = retweeted_id
            status.username = username
            status.avatar = avatar
            status.text = post['text']
            status.in_reply_to_id = in_reply_to_id
            status.in_reply_to_user = in_reply_to_user
            status.is_favorite = fav
            status.is_protected = protected
            status.is_verified = verified
            status.reposted_by = reposted_by
            status.datetime = self.get_str_time(post['created_at'])
            status.timestamp = self.get_int_time(post['created_at'])
            status.entities = self.get_entities(post)
            status._type = _type
            status.account_id = self.account_id
            status.is_own = (username.lower() == self.uname.lower())
            status.retweeted = retweeted
            status.set_display_id(column_id)
            status.get_source(source)
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

    def get_entities(self, tweet):
        if 'entities' in tweet:
            entities = {
                'urls': [],
                'hashtags': [],
                'mentions': [],
                'groups': [],
            }
            for mention in tweet['entities']['user_mentions']:
                text = '@' + mention['screen_name']
                entities['mentions'].append(Entity(self.account_id,
                                            mention['screen_name'], text,
                                            text))

            for url in tweet['entities']['urls']:
                try:
                    expanded_url = url['expanded_url']
                except KeyError:
                    expanded_url = url['url']

                try:
                    display_url = ''.join(['http://', url['display_url']])
                except KeyError:
                    display_url = url['url']

                entities['urls'].append(Entity(self.account_id, expanded_url,
                                        display_url, url['url']))

            if 'media' in tweet['entities']:
                for url in tweet['entities']['media']:
                    display_url = ''.join(['http://', url['display_url']])
                    entities['urls'].append(Entity(self.account_id,
                                            url['media_url'], display_url,
                                            url['url']))

            for ht in tweet['entities']['hashtags']:
                text = ''.join(['#', ht['text']])
                url = "%s%s" % (self.hashtags_url, ht['text'])
                entities['hashtags'].append(Entity(self.account_id, url, text,
                                            text))
        return entities
