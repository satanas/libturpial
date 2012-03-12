# -*- coding: utf-8 -*-

""" pic.twitter.com show media content service """
#
# Author: Wil Alvarez (aka satanas)
# 2012-03-10

import traceback

from libturpial.api.models.mediacontent import *
from libturpial.api.services.showmedia.base import *
from libturpial.api.interfaces.service import ServiceResponse

class PicTwitterMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?(p.twimg.com|pic.twitter.com)"

    def do_service(self, url):
        try:
            rawimg = self._get_content_from_url(url)
            return ServiceResponse(MediaContent(IMAGE_CONTENT, url, rawimg))
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem showing media content'))
