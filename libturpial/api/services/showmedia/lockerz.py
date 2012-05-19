# -*- coding: utf-8 -*-

"""Lockers show media content service"""
#
# Author: William Cabrera (aka willicab)
# 2012-03-13

import traceback

from libturpial.api.models.mediacontent import *
from libturpial.api.services.showmedia.base import *
from libturpial.api.interfaces.service import ServiceResponse

class LockerzMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?lockerz.com"

    def do_service(self, url):
        try:
            page_content = self._get_content_from_url(url)
            media_content, nombre = self.__find_url_in_html(page_content, url)
            rawimg = self._get_content_from_url(media_content)
            return ServiceResponse(MediaContent(IMAGE_CONTENT, nombre, rawimg))
        except Exception, error:
            pass
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, errmsg=_('Problem showing media content'))

    def __find_url_in_html(self, html, url):
        path = '<img id="photo" src="'
        start = html.find(path) + len(path)
        end = html.find('" data-url="' + url + '">', start, len(html))
        link1 = html[start:end]
        #print "link1: " + link1
        end2 = link1.find('" title="', 0, len(link1))
        link2 = link1[0:end2]
        #print "link2: " + link2
        return link2, link2.split('/')[-1]
