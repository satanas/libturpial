# -*- coding: utf-8 -*-

""" Module to handle rate limits information """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 18, 2011

class RateLimit:
    def __init__(self):
        self.hourly_limit = None
        self.remaining_hits = None
        self.reset_time = None
        self.reset_time_in_seconds = None
