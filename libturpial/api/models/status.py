# -*- coding: utf-8 -*-

import xml.sax.saxutils as saxutils

from libturpial.api.models.client import Client
from libturpial.common import StatusType, CLIENT_PATTERN


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
        self.favorited = False  # Status has been favorited
        self.protected = False  # Status comes from a protected account
        self.verified = False   # Status comes from a verified account
        self.repeated = False   # Status has been repeated by user
        self.is_own = False     # Indicate if the user is the author of the status
        self.reposted_by = None     # Indicates if it is a repeated status
        self.reposted_count = None  # How much repeats get the status
        self.datetime = None    # Store the date/time showed for the view
        self._type = None
        self.account_id = None
        self.entities = {}
        self.retweeted_id = None
        self.display_id = None

    def get_mentions(self):
        """
        Returns all usernames mentioned in status (even the author of the 
        status)
        """
        account = self.account_id.split('-')[0]
        mentions = [self.username]
        if 'mentions' in self.entities:
            for user in map(lambda x: x.display_text[1:], self.entities['mentions']):
                if user.lower() != account.lower() and user not in mentions:
                    mentions.append(user)
        return mentions

    def set_display_id(self, column_id):
        self.display_id = "%s-%s-%s" % (self.account_id, self.id_, column_id)

    def is_direct(self):
        return (self._type == StatusType.DIRECT)

    def get_protocol_id(self):
        return self.account_id.split('-')[1]

    def get_source(self, source):
        """
        Parse the source text in the status and store it in a 
        :class:`libturpial.api.models.client.Client` object.
        """
        if not source:
            self.source = None
        else:
            text = saxutils.unescape(source)
            text = text.replace('&quot;', '"')
            if text == 'web':
                self.source = Client(text, "http://twitter.com")
            else:
                rtn = CLIENT_PATTERN.search(text)
                if rtn:
                    self.source = Client(rtn.groups()[1], rtn.groups()[0])
                else:
                    self.source = Client(source, None)
