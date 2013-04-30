# -*- coding: utf-8 -*-

"""Via.me show media content service"""
#
# Author: Wil Alvarez (aka satanas)
# 2012-09-30

import json
import traceback

from libturpial.api.models.media import *
from libturpial.lib.services.media.preview.base import *
from libturpial.lib.interfaces.service import ServiceResponse

CLIENT_ID = '3ycgz7gzer80068s80t4xl1cs'


class ViameMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?via.me"

    def do_service(self, url):
        try:
            post_id = url.split('/')[-1][1:]
            req_url = 'https://api.via.me/v1/posts/%s?client_id=%s' % (post_id,
                                                                       CLIENT_ID)
            self.log.debug('Via.me url: %s' % req_url)
            resp = json.loads(self._get_content_from_url(req_url))
            media_content_url = resp['response']['post']['media_url']
            self.log.debug('Via.me response: %s' % media_content_url)
            rawimg = self._get_content_from_url(media_content_url)
            return ServiceResponse(MediaContent(IMAGE_CONTENT, url, rawimg))
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True,
                                   errmsg=_('Problem showing media content'))
