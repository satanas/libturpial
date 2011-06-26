# -*- coding: utf-8 -*-

""" Module to handle profiles information """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 12, 2011

class Profile:
    DEFAULT_LINK_COLOR = '#0F0F85'
    
    def __init__(self):
        self.id_ = None
        self.fullname = None
        self.username = None
        self.avatar = None
        self.location = ''
        self.url = ''
        self.bio = ''
        self.following = None
        self.followers_count = None
        self.friends_count = None
        self.password = None
        self.link_color = None
        self.statuses_count = None
        self.last_update = None
        self.last_update_id = None
        self.recent_updates = []
        self.tmp_avatar_path = None
