# -*- coding: utf-8 -*-

"""Yforg show media content service"""
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# 2012-03-10

import traceback
from showmediaservice import *

class YfrogMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?yfrog.com"
        
    def do_service(self, url):
        try:
            media_content_url = "%s:medium" % url
            rawimg = self._get_raw_image_from_url(media_content_url)
            return ServiceResponse(rawimg)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem showing media content'))
