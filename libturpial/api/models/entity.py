# -*- coding: utf-8 -*-

class Entity:
    """
    Sometimes a :class:`libturpial.api.models.status.Status` can content
    mentions, URLs, hashtags and other class of interactuable objects, so 
    this class models that data in a structured way

    :ivar account_id: Id of the account that holds the status
    :ivar url: A possible URL for the media/content
    :ivar display_text: Text that must be displayed to user
    :ivar search_for: Text that must be used to search this object
    """
    def __init__(self, account_id, url, text, search):
        self.account_id = account_id
        self.url = url
        self.display_text = text
        self.search_for = search
