# -*- coding: utf-8 -*-

class Entity:
    """
    A :class:`libturpial.api.model.status.Status` can potentially contents
    mentions, URLs, hashtags and other so this class models that data in a 
    parsed and structured way
    """
    def __init__(self, account_id, url, text, search):
        self.account_id = account_id
        self.url = url
        self.display_text = text
        self.search_for = search
