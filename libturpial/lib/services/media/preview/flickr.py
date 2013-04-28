# -*- coding: utf-8 -*-

"""Via.me show media content service"""
#
# Author: Wil Alvarez (aka satanas)
# 2012-09-30

import httplib
import traceback

from libturpial.api.models.mediacontent import *
from libturpial.api.services.showmedia.base import *
from libturpial.api.interfaces.service import ServiceResponse

API_KEY = '0cfe8dd171816a484b9def6cc27aec31'

class FlickrMediaContent(ShowMediaService):
    def __init__(self):
        ShowMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?flic.kr"
        self.xml_pattern = re.compile('label="Original" width="(.*)" height="(.*)" source="(.*)" url="(.*)" media="(.*)"')
        self.resp_pattern = re.compile('/photos/(.*)/(.*)/')

    def do_service(self, url):
        try:
            c = httplib.HTTPConnection('flic.kr')
            while 1:
                # Resolv all possible redirects
                c.request('GET', url)
                r = c.getresponse()
                l = r.getheader('Location')
                x = self.resp_pattern.search(l)
                if x:
                    photo_id = x.groups(0)[1]
                    break
                else:
                    url = l
                    self.log.debug('Flic.kr redirect: %s' % url)

            req_url = 'http://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=%s&photo_id=%s' % (API_KEY, photo_id)
            self.log.debug('Flic.kr url: %s' % req_url)
            xml = self._get_content_from_url(req_url)
            resp = self.xml_pattern.search(xml)
            media_content_url = resp.groups(0)[2]
            self.log.debug('Flic.kr response: %s' % media_content_url)
            rawimg = self._get_content_from_url(media_content_url)
            return ServiceResponse(MediaContent(IMAGE_CONTENT, url, rawimg))
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, errmsg=_('Problem showing media content'))
