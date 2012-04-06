# -*- coding: utf-8 -*-

"""Imgur show media content service"""
#
# Author: William Cabrera (aka willicab)
# 2012-03-28

import traceback
#from showmediaservice import *
from libturpial.api.models.mediacontent import *
from libturpial.api.services.showmedia.base import *
from libturpial.api.interfaces.service import ServiceResponse

class ImgurMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?imgur.com"

    def do_service(self, url):
        try:
            page_content = self._get_content_from_url(url)
            media_content, nombre = self.__find_url_in_html(page_content)
            rawimg = self._get_content_from_url(media_content)
            return ServiceResponse(MediaContent(IMAGE_CONTENT, nombre, rawimg))
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, errmsg=_('Problem showing media content'))

    def __find_url_in_html(self, html):
        path = '<link rel="image_src" href="'
        start = html.find(path) + len(path)
        end = html.find('" />', start, len(html))
        return html[start:end], html[start:end].split('/')[-1]
