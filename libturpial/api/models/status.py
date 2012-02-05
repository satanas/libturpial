# -*- coding: utf-8 -*-

""" Module to handle statuses information """
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

from libturpial.common import StatusType

class Status:
    def __init__(self):
        self.id_ = None
        self.text = None
        self.username = None
        self.avatar = None
        self.source = None
        self.timestamp = None   # Store the timestamp in Unix time
        self.in_reply_to_id = None
        self.in_reply_to_user = None
        self.is_favorite = False
        self.is_protected = False
        self.is_verified = False
        self.reposted_by = None
        self.reposted_count = None
        self.datetime = None    # Store the date/time showed for the view
        self._type = None
        self.account_id = None
        self.is_own = False
        self.entities = {}
        self.retweeted = False
        self.retweeted_id = None
        self.display_id = None
    
    def get_reply_mentions(self):
        account = '@' + self.account_id.split('-')[0]
        count = [self.username]
        if self.entities.has_key('mentions'):
            for user in self.entities['mentions']:
                if user.display_text != account:
                    count.append(user.display_text[1:])
            return count
        else:
            return []
    
    def set_display_id(self, column_id):
        self.display_id = "%s-%s-%s" % (self.account_id, self.id_, column_id)
    
    def is_direct(self):
        return (self._type == StatusType.DIRECT)
