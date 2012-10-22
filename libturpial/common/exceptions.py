# -*- coding: utf-8 -*-

""" Module to handle custom exceptions for Turpial """
#
# Author: Wil Alvarez (aka Satanas)
# Jan 07, 2012


class URLShortenError(Exception):
    def __init__(self, message):
        self.message = message


class NoURLException(Exception):
    def __init__(self):
        self.message = 'No URL to short'


class UploadImageError(Exception):
    def __init__(self, message):
        self.message = message
