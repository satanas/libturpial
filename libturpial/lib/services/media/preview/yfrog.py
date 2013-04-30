# -*- coding: utf-8 -*-

"""Yfrog show media content service"""
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# 2012-03-10

import traceback

from libturpial.api.models.media import *
from libturpial.lib.services.media.preview.base import *
from libturpial.lib.interfaces.service import ServiceResponse


class YfrogMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?yfrog.com"

    def do_service(self, url):
        try:
            media_content_url = "%s:medium" % url
            rawimg = self._get_content_from_url(media_content_url)
            return ServiceResponse(MediaContent(IMAGE_CONTENT, url, rawimg))
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True,
                                   errmsg=_('Problem showing media content'))
