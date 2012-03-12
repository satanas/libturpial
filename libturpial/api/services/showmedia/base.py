# -*- coding: utf-8 -*-

"""Common interface for show media content services"""
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# 2010-08-01

import os
import re
import httplib
import urllib2
import logging

from libturpial.api.interfaces.service import GenericService

IMAGE_CONTENT = 0
VIDEO_CONTENT = 1

class MediaContent(object):
    def __init__(self, type, name, content, info={}):
        self.type = type
        self.name = name
        self.content = content
        self.info = info
    
    def save_content(self):
        try:
            fd = open(self.info['path'], 'wb')
            fd.write(self.content)
            fd.close()
        except KeyError:
            pass

class ShowMediaService(GenericService):
    def __init__(self):
        self.log = logging.getLogger('Service')
        self.url_pattern = ""

    def do_service(self, url):
        raise NotImplementedError

    def _get_content_from_url(self, url):
        return urllib2.urlopen(url).read()

    def _get_id_from_url(self, url):
        parts = url.split("/")
        return parts[-1]

    def can_manage_url(self, url):
        regex = re.compile(self.url_pattern)
        if regex.search(url):
            return True
        return False
