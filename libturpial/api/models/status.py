# -*- coding: utf-8 -*-

import xml.sax.saxutils as saxutils

from libturpial.common import CLIENT_PATTERN
from libturpial.api.models.client import Client


class Status:
    """
    This model represents and holds all the information of a status.

    :ivar id_: Status id
    :ivar account_id: Id of the account associated to this status
    :ivar text: Text of the status
    :ivar username: Name of the user that updated the status
    :ivar avatar: Display image of the user that updated the status
    :ivar source: Client used to upload this status
    :ivar timestamp: Time of publishing of this status (Unix time)
    :ivar in_reply_to_id: Contains the id of the status answered (if any)
    :ivar in_reply_to_user: Contains the user answered with status (if any)
    :ivar is_favorite: `True` if this status has been marked as favorite.
                       `False` otherwise
    :ivar is_protected: `True` if this status is from a protected account.
                        `False` otherwise
    :ivar is_verified: `True` if this status is from a verified account.
                       `False` otherwise
    :ivar repeated: `True` if this status has been repeated (retweeted) by you.
                    `False` otherwise
    :ivar repeated_by: More users that have repeated this status
    :ivar repeated_count: How much times this status has been repeated
    :ivar original_status_id: Id of the original status (not-repeated)
    :ivar created_at: Original timestamp from the service
    :ivar datetime: Humanized representation of the date/time of this status
    :ivar is_own: `True` if the status belongs to the same user of the
                  associated account. `False` otherwise
    :ivar entities: A dict with all the entities found in status
    :ivar type_: Status type.

    Sometimes a status can hold one or more entities (URLs, hashtags, etc). In this
    case the entities variable will store a dict with lists for each category.
    For example:

    >>> status = Status()
    >>> status.entities
    {'urls': [], 'hashtags': [], 'mentions': [], 'groups': []}

    A status can handle two possible types:
    :class:`libturpial.api.models.status.Status.NORMAL` for regular statuses
    or :class:`libturpial.api.models.status.Status.DIRECT` for private
    (direct) statuses.
    """

    NORMAL = 0x1
    DIRECT = 0x2

    def __init__(self):
        self.id_ = None
        self.text = None
        self.username = None
        self.avatar = None
        self.source = None
        self.timestamp = None  # Store the timestamp in Unix time
        self.in_reply_to_id = None
        self.in_reply_to_user = None
        self.is_favorite = False  # Status has been favorited
        self.is_protected = False  # Status comes from a protected account
        self.is_verified = False   # Status comes from a verified account
        self.repeated = False   # Status has been repeated by user
        self.repeated_by = None     # Indicates if it is a repeated status
        self.repeated_count = None  # How much repeats get the status
        self.datetime = None    # Store the date/time in GMT
        self.is_own = False     # Indicate if the user is the author of the status
        self.type_ = None
        self.account_id = None
        self.entities = {}
        self.original_status_id = None
        self.created_at = None
        self.local_datetime = None  # Store the timestamp as long integer in local time

    def __eq__(self, status):
        return self.id_ == status.id_

    def __ne__(self, status):
        return self.id_ != status.id_

    def get_mentions(self):
        """
        Returns all usernames mentioned in status (even the author of the
        status)
        """
        account = self.account_id.split('-')[0]
        mentions = [self.username]
        if 'mentions' in self.entities:
            for user in map(lambda x: x.display_text[1:],
                            self.entities['mentions']):
                if user.lower() != account.lower() and user not in mentions:
                    mentions.append(user)
        return mentions

    def is_direct(self):
        """
        Return `True` if this status is a direct message
        """
        return self.type_ == self.DIRECT

    def get_protocol_id(self):
        """
        Return the *protocol_id* associated to this status
        """
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
