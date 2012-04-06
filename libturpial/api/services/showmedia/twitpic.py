# -*- coding: utf-8 -*-

"""Twitpic show media content service"""
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# 2012-03-08

import traceback

from libturpial.api.models.mediacontent import *
from libturpial.api.services.showmedia.base import *
from libturpial.api.interfaces.service import ServiceResponse

class TwitpicMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?twitpic.com"

    def do_service(self, url):
        try:
            media_id = self._get_id_from_url(url)
            media_content_url =  "http://twitpic.com/show/full/%s.png" % media_id
            rawimg = self._get_content_from_url(media_content_url)
            return ServiceResponse(MediaContent(IMAGE_CONTENT, url, rawimg))
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, errmsg=_('Problem showing media content'))
