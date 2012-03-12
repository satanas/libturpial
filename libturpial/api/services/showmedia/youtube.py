# -*- coding: utf-8 -*-

"""YouTube show media content service"""
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# 2012-03-12

import traceback

from libturpial.api.models.mediacontent import *
from libturpial.api.services.showmedia.base import *
from libturpial.api.interfaces.service import ServiceResponse

class YouTubeMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?(youtu.be|youtube.com)"

    def do_service(self, url):
        try:
            content = self._get_id_from_url(url)
            path = "https://www.youtube.com/embed/%s?wmode=opaque" % content
            info = {}
            info['width'] = 436
            info['height'] = 357
            return ServiceResponse(MediaContent(VIDEO_CONTENT, url, content, path, info))
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem showing media content'))

    def _get_id_from_url(self, url):
        if url.find("youtu.be") != -1:
            return ShowMediaService._get_id_from_url(self, url)
        else:
            return url.split("v=")[1]
