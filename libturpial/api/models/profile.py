# -*- coding: utf-8 -*-


class Profile:
    """
    This model handles all the information stored for a user profile.

    :ivar id_: Profile id
    :ivar account_id: Account id that fetched this profile
    :ivar fullname: Full name of the user
    :ivar avatar: Display image
    :ivar location: User location
    :ivar url: User URL
    :ivar bio: User bio or description
    :ivar following: Indicate if the user is following to the account_id owner (`True`or `False`)
    :ivar followed_by: Indicate if the user is followed by the account_id owner (`True`or `False`)
    :ivar follow_request: Indicate if there is a pending follow request of this profile
    :ivar followers_count: Number of followers of this user
    :ivar friends_count: Number of friends of this user
    :ivar favorites_count: Number of favorite statuses of this user
    :ivar statuses_count: Number of statuses this user has done
    :ivar link_color: Color used to highlight entities (URLs, hashtags, etc)
    :ivar last_update: Text of the last status updated
    :ivar last_update_id: Id of the last status updated
    :ivar protected: Indicate if the profile is protected (`True`or `False`)
    :ivar verified: Indicate if the profile is verified (`True`or `False`)

    """

    def __init__(self):
        self.id_ = None
        self.account_id = None
        self.fullname = None
        self.username = None
        self.avatar = None
        self.location = ''
        self.url = ''
        self.bio = ''
        self.following = None
        self.followed_by = None
        self.follow_request = False
        self.followers_count = 0
        self.friends_count = 0
        self.link_color = None
        self.statuses_count = 0
        self.favorites_count = 0
        self.last_update = None
        self.last_update_id = None
        self.recent_updates = []
        self.tmp_avatar_path = None
        self.protected = False
        self.verified = False
        self.muted = False

    def __repr__(self):
        return "libturpial.api.models.Profile %s" % (self.username)

    def is_me(self):
        """
        Return `True` if the username of the profile is the same of the
        associated account, otherwise `False`. This method can be useful to 
        determinate if a status belongs to given account.
        """
        if self.username == self.account_id.split('-')[0]:
            return True
        return False

    def get_protocol_id(self):
        """
        Returns the *protocol_id* for this profile
        """
        if self.account_id:
            return self.account_id.split('-')[1]
        else:
            return None
