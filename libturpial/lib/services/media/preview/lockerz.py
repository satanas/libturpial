# -*- coding: utf-8 -*-

"""Lockers show media content service"""
#
# Author: William Cabrera (aka willicab), Wil Alvarez (aka satanas)
# 2012-03-13

import traceback

from libturpial.api.models.media import *
from libturpial.lib.services.media.preview.base import *
from libturpial.lib.interfaces.service import ServiceResponse

class LockerzMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?lockerz.com"

    def do_service(self, url):
        try:
            url2 = 'http://api.plixi.com/api/tpapi.svc/imagefromurl?url=%s&size=big' % url
            self.log.debug('Lockerz url: %s' % url2)
            rawimg = self._get_content_from_url(url2)
            return ServiceResponse(MediaContent(IMAGE_CONTENT, url, rawimg))
        except Exception, error:
            self.log.error("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, errmsg=_('Problem showing media content'))
