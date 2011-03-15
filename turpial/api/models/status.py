# -*- coding: utf-8 -*-

""" Module to handle statuses information """
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

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
        self.reposted_by = None
        self.datetime = None    # Store the date/time showed for the view
        self._type = None
        self.account_id = None
        self.is_own = False
