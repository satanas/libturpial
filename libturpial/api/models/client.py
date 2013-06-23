# -*- coding: utf-8 -*-

class Client:
    """
    This class models the information of the client of a given status
    """
    def __init__(self, name=None, url=None):
        self.name = name
        self.url = url
