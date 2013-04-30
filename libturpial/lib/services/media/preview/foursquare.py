# -*- coding: utf-8 -*-

"""Foursquare show media content service"""
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# 2012-03-12

import urllib
import traceback

from libturpial.api.models.media import *
from libturpial.lib.services.media.preview.base import *
from libturpial.lib.interfaces.service import ServiceResponse

class FoursquareMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?4sq.com"

    def do_service(self, url):
        try:
            long_url = urllib.urlopen(url).geturl()
            url_parts = long_url.split("foursquare.com")
            path = "%s%s%s" % (url_parts[0], "foursquare.com/oembed", url_parts[1])
            info = {}
            info['width'] = 436
            info['height'] = 357
            return ServiceResponse(MediaContent(MAP_CONTENT, url, long_url, path, info))
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, errmsg=_('Problem showing media content'))
