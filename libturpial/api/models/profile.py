# -*- coding: utf-8 -*-


class Profile:
    """
    This model handles a user profile.
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
        self.follow_request = False
        self.followers_count = None
        self.friends_count = None
        self.password = None
        self.link_color = None
        self.statuses_count = None
        self.favorites_count = 0
        self.last_update = None
        self.last_update_id = None
        self.recent_updates = []
        self.tmp_avatar_path = None
        self.protected = False
        self.verified = False
        self.muted = False

    def is_me(self):
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
