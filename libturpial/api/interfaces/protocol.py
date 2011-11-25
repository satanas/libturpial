# -*- coding: utf-8 -*-

"""Generic module to implement microblogging protocols in Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

import re
import time
import logging
import datetime
import xml.sax.saxutils as saxutils

from libturpial.api.interfaces.http import TurpialHTTP

class Protocol(TurpialHTTP):
    ''' Base class to define basic functions that must have any protocol
    implementation '''
    
    HASHTAG_PATTERN = re.compile('(?<![\w])#[\wáéíóúÁÉÍÓÚñÑçÇ]+')
    MENTION_PATTERN = re.compile('(?<![\w])@[\w]+')
    CLIENT_PATTERN = re.compile('<a href="(.*?)">(.*?)</a>')
    # According to RFC 3986 - http://www.ietf.org/rfc/rfc3986.txt
    URL_PATTERN = re.compile('((?<!\w)(http://|ftp://|https://|www\.)[-\w._~:/?#\[\]@!$&\'()*+,;=]*)')
    
    def __init__(self, account_id, name, api_url, search_url, tags_url=None, 
        groups_url=None, profiles_url=None, post_actions=[]):
        TurpialHTTP.__init__(self, post_actions)
        
        self.urls['api'] = api_url
        self.urls['search'] = search_url
        if tags_url:
            self.urls['tags'] = tags_url
        if tags_url:
            self.urls['groups'] = groups_url
        if tags_url:
            self.urls['profiles'] = profiles_url
        
        self.log = logging.getLogger(name)
        self.log.debug('Started')
    
    # ------------------------------------------------------------
    # Time related methods. Overwrite if necesary
    # ------------------------------------------------------------
    def convert_time(self, str_datetime):
        ''' Take the date/time and convert it into Unix time'''
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
        
        i_hate_timezones = time.timezone
        if (time.daylight):
            i_hate_timezones = time.altzone
        
        dt = datetime.datetime(*d.timetuple()[:-3]) - \
             datetime.timedelta(seconds=i_hate_timezones)
        return dt.timetuple()
        
    def get_str_time(self, strdate):
        t = self.convert_time(strdate)
        return time.strftime('%b %d, %I:%M %p', t)
        
    def get_int_time(self, strdate):
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
        
        urls = []
        for item in self.URL_PATTERN.findall(text):
            url = item[0]
            # Removes the last parenthesis
            if url[-1] == ')':
                url = url[:-1]
            urls.append(url)
        entities['urls'] = urls
        
        hashtags = []
        for item in self.HASHTAG_PATTERN.findall(text):
            hashtags.append(item)
        entities['hashtags'] = hashtags
        
        mentions = []
        for item in self.MENTION_PATTERN.findall(text):
            mentions.append(item)
        entities['mentions'] = mentions
        return entities
    
    def get_source(self, source):
        if not source:
            return None
        text = saxutils.unescape(source)
        text = text.replace('&quot;', '"')
        if text == 'web':
            return text
        rtn = self.CLIENT_PATTERN.search(text)
        if rtn:
            return rtn.groups()[1]
        return source
    
    # ------------------------------------------------------------
    # Methods to be overwritten
    # ------------------------------------------------------------
    
    def json_to_profile(self, response):
        ''' Returns a Profile object from a JSON response '''
        raise NotImplementedError
    
    def json_to_status(self, response):
        ''' Returns a Status object from a JSON response '''
        raise NotImplementedError
        
    def json_to_ratelimit(self, response):
        ''' Returns a RateLimit object from a JSON response '''
        raise NotImplementedError
        
    def json_to_list(self, response):
        ''' Returns a List object from a JSON response '''
        raise NotImplementedError
        
    def response_to_statuses(self, response, mute=False):
        ''' Take the server response and transform into an array of Status 
        objects inside a Response object '''
        raise NotImplementedError
        
    def response_to_profiles(self, response):
        ''' Take the server response and transform into an array of Profile 
        objects inside a Response object '''
        raise NotImplementedError
        
    def auth(self, username, password):
        raise NotImplementedError
        
    def get_timeline(self, count):
        ''' 
        Fetch the timeline from the server 
        '''
        raise NotImplementedError
        
    def get_replies(self, count):
        ''' 
        Fetch the mentions from the server 
        '''
        raise NotImplementedError
        
    def get_directs(self, count):
        ''' 
        Fetch the directs from the server 
        '''
        raise NotImplementedError
        
    def get_sent(self, count):
        ''' 
        Fetch the sent messages from the server 
        '''
        raise NotImplementedError
        
    def get_favorites(self, count):
        ''' 
        Fetch the favorites from the server 
        '''
        raise NotImplementedError
        
    def get_public_timeline(self, count):
        ''' 
        Fetch the public timeline from the server 
        '''
        raise NotImplementedError
        
    def get_lists(self, username):
        ''' 
        Fetch all user lists for service
        '''
        raise NotImplementedError
        
    def get_list_statuses(self, list_id):
        ''' 
        Fetch all statuses for a specific list
        '''
        raise NotImplementedError
    
    def get_conversation(self, id_):
        ''' 
        Fetch the whole conversation related to a single status
        '''
        raise NotImplementedError
        
    def get_friends(self):
        ''' 
        Fetch the whole friends list
        '''
        raise NotImplementedError
        
    def get_profile(self, user):
        ''' 
        Fetch an especific user profile
        '''
        raise NotImplementedError
        
    def get_blocked(self):
        ''' 
        Fetch the list of blocked users
        '''
        raise NotImplementedError
        
    def get_rate_limits(self):
        ''' 
        Fetch the rate limits for the service
        '''
        raise NotImplementedError
        
    def update_profile(self, profile_args):
        ''' 
        Update the user profile
        '''
        raise NotImplementedError
        
    def update_status(self, text, in_reply_to_id=None):
        ''' 
        Post an update
        '''
        raise NotImplementedError
    
    def destroy_status(self, id_):
        ''' 
        Destroy a posted update
        '''
        raise NotImplementedError
        
    def repeat(self, id_):
        ''' 
        Repeat to all your friends an update posted by somebody
        '''
        raise NotImplementedError
        
    def mark_favorite(self, id_):
        ''' 
        Mark an update as favorite
        '''
        raise NotImplementedError
        
    def unmark_favorite(self, id_):
        ''' 
        Unmark an update as favorite
        '''
        raise NotImplementedError
        
    def follow(self, user):
        ''' 
        Follow somebody
        '''
        raise NotImplementedError
        
    def unfollow(self, user):
        ''' 
        Unfollow somebody
        '''
        raise NotImplementedError
        
    def send_direct(self, user, text):
        # FIXME: Implementar
        #raise NotImplementedError
        pass
        
    def destroy_direct(self, id_):
        ''' 
        Destroy a direct message
        '''
        raise NotImplementedError
        
    def block(self, user):
        ''' 
        Blocks the specified user
        '''
        raise NotImplementedError
    
    def unblock(self, user):
        ''' 
        Unblocks the specified user
        '''
        raise NotImplementedError
    
    def report_spam(self, user):
        ''' 
        Blocks and report the specified user as spammer
        '''
        raise NotImplementedError
        
    def search(self, query, count):
        ''' 
        Execute a search query in server
        '''
        raise NotImplementedError
    
    def trends(self):
        ''' 
        Search for trends
        '''
        raise NotImplementedError
    
    def is_friend(self, user):
        ''' 
        Returns True is user follows current account, False otherwise
        '''
        raise NotImplementedError
    
