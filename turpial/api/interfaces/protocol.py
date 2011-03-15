# -*- coding: utf-8 -*-

"""Módulo genérico para implementar protocolos de microblogging en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

import time
import logging
import datetime

from turpial.api.interfaces.http import TurpialHTTP
from turpial.api.protocols.twitter.globals import POST_ACTIONS

class Protocol(TurpialHTTP):
    ''' Base class to define basic functions that must have any protocol
    implementation '''
    def __init__(self, account_id, name, api_url, search_url, tags_url=None, 
        groups_url=None, profiles_url=None):
        TurpialHTTP.__init__(self, POST_ACTIONS)
        
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
    
    # ------------------------------------------------------------
    # Methods to be overwritten
    # ------------------------------------------------------------
    
    def json_to_profile(self, response):
        ''' Returns a Profile object from a JSON response '''
        raise NotImplementedError
    
    def json_to_status(self, response):
        ''' Returns a Status object from a JSON response '''
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
        Returns: a Response object with self.timeline
        '''
        raise NotImplementedError
        
    def get_replies(self, count):
        ''' 
        Fetch the mentions from the server 
        Returns: a Response object with self.replies
        '''
        raise NotImplementedError
        
    def get_directs(self, count):
        ''' 
        Fetch the directs from the server 
        Returns: a Response object with self.directs
        '''
        raise NotImplementedError
        
    def get_sent(self, count):
        ''' 
        Fetch the sent messages from the server 
        Returns: a Response object with self.sent
        '''
        raise NotImplementedError
        
    def get_favorites(self, count):
        ''' 
        Fetch the favorites from the server 
        Returns: a Response object with self.favorites
        '''
        raise NotImplementedError
        
    def get_rate_limits(self):
        ''' 
        Fetch the rate limits from API 
        Returns: a Response object with a RateLimit
        '''
        raise NotImplementedError
        
    def get_conversation(self, id):
        ''' 
        Fetch the whole conversation from a single status
        Returns: a Response object of statuses
        '''
        raise NotImplementedError
        
    def get_friends_list(self):
        ''' 
        Fetch the whole friends list
        Returns: a Response object of profiles
        '''
        raise NotImplementedError
        
    def get_profile(self, user):
        ''' 
        Fetch an especific user profile
        Returns: a Response object with the profile
        '''
        raise NotImplementedError
        
    def update_profile(self, name, url, bio, location):
        ''' 
        Update the user profile
        Returns: a Response object with the user profile
        '''
        raise NotImplementedError
        
    def update_status(self, in_reply_to_id):
        ''' 
        Post an update
        Returns: a Response object with the posted status
        '''
        raise NotImplementedError
        
    def destroy_status(self, id):
        ''' 
        Destroy a posted update
        Returns: four Response object with self.timeline, self.favorites
        
        Implement this function in this way:
        
        self.to_del.append(id)
        # All the dirty work goes here
        self._destroy_status(id)
        '''
        raise NotImplementedError
        
    def repeat(self, id):
        ''' 
        Repeat to all your friends an update posted by somebody
        Returns: a Response object with self.timeline
        '''
        raise NotImplementedError
        
    def mark_favorite(self, id):
        ''' 
        Mark an update as favorite
        Returns: three Response object with self.timeline, self.replies,
        self.favorites
        
        Implement this function in this way:
        
        self.to_fav.append(id)
        # All the dirty work goes here
        self._set_status_favorite(id)
        '''
        raise NotImplementedError
        
    def unmark_favorite(self, id):
        ''' 
        Unmark an update as favorite
        Returns: three Response object with self.timeline, self.replies,
        self.favorites
        
        Implement this function in this way:
        
        self.to_unfav.append(id)
        # All the dirty work goes here
        self._unset_status_favorite(id)
        '''
        raise NotImplementedError
        
    def follow(self, user):
        ''' 
        Follow somebody
        Returns: four objects: single_friend_list, self.profile, user and True
        '''
        raise NotImplementedError
        
    def unfollow(self, user):
        ''' 
        Unfollow somebody
        Returns: four objects: single_friend_list, self.profile, user and False
        '''
        raise NotImplementedError
        
    def send_direct(self, user, text):
        # FIXME: Implementar
        #raise NotImplementedError
        pass
        
    def destroy_direct(self, id):
        ''' 
        Destroy a direct message
        Returns: a Response object with self.directs
        
        Implement this function in this way:
        
        self.to_del.append(id)
        # All the dirty work goes here
        self._destroy_status(id)
        '''
        raise NotImplementedError
        
    def search(self, query, count):
        ''' 
        Execute a query in server
        Returns: a Response object with query results
        '''
        raise NotImplementedError
        
    def get_lists(self):
        ''' 
        Fetch all lists for the user in that protocol
        Returns: a Response object with query results
        '''
        raise NotImplementedError
        
    def get_list_statuses(self, args):
        ''' 
        Fetch all statuses for a specific list
        Returns: a Response object with query results
        '''
        raise NotImplementedError
