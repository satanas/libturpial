# -*- coding: utf-8 -*-

"""Instagr.am show media content service"""
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# 2012-03-10

import traceback
from showmediaservice import *

class InstagramMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?instagr.am"
        
    def do_service(self, url):
        try:
            page_content = self._get_content_from_url(url)
            media_content_url = self.find_url_in_html(page_content)
            rawimg = self._get_content_from_url(media_content_url)
            return ServiceResponse(rawimg)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem showing media content'))

    def find_url_in_html(self, html):
        path = '<img class="photo" src="'
        start = html.find(path) + len(path)
        end = html.find('" />', start, len(html))
        return html[start:end]
