# -*- coding: utf-8 -*-

"""Imgur show media content service"""
#
# Author: William Cabrera (aka willicab)
# 2012-03-28

import json
import traceback

from libturpial.api.models.mediacontent import *
from libturpial.api.services.showmedia.base import *
from libturpial.api.interfaces.service import ServiceResponse

API_KEY = '7ea1d30de2992c783a567df86faa388e'


class ImgurMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?imgur.com"

    def do_service(self, url):
        try:
            img_id = url.split('/')[-1].split('.')[0]
            req_url = 'https://api.imgur.com/2/image/%s.json' % (img_id)
            self.log.debug('Imgur.com url: %s' % req_url)
            resp = json.loads(self._get_content_from_url(req_url))
            media_content_url = resp['image']['links']['original']
            self.log.debug('Imgur.com response: %s' % media_content_url)
            rawimg = self._get_content_from_url(media_content_url)
            return ServiceResponse(MediaContent(IMAGE_CONTENT, url, rawimg))
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True,
                                   errmsg=_('Problem showing media content'))

    def __find_url_in_html(self, html):
        path = '<link rel="image_src" href="'
        start = html.find(path) + len(path)
        end = html.find('" />', start, len(html))
        return html[start:end], html[start:end].split('/')[-1]
