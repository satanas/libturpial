# -*- coding: utf-8 -*-

"""Pinterest show media content service"""
#
# Author: William Cabrera (aka willicab)
# 2012-03-28

import traceback
from showmediaservice import *
from libturpial.api.models.mediacontent import *
from libturpial.api.services.showmedia.base import *
from libturpial.api.interfaces.service import ServiceResponse

class PinterestMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?pinterest.com"
        
    def do_service(self, url):
        try:
            page_content = self._get_content_from_url(url)
            url = url[:-1]
            id_url = url.split('/')[-1]
            media_content, nombre = self.__find_url_in_html(page_content, id_url)
            rawimg = self._get_content_from_url(media_content)
            return ServiceResponse(MediaContent(IMAGE_CONTENT, nombre, rawimg))
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem showing media content'))

    def __find_url_in_html(self, html, id_url):
        pass
        path = "data-id=\"%s\"><img src=\"" % (id_url)
        start = html.find(path) + len(path)
        end = html.find('" id="pinCloseupImage" alt="Pinned Image" />', start, len(html))
        return html[start:end], html[start:end].split('/')[-1]
