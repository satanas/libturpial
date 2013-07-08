# -*- coding: utf-8 -*-

"""Flic.kr show media content service"""

import httplib
import re

from libturpial.api.models.media import Media
from libturpial.lib.services.media.preview.base import PreviewMediaService

API_KEY = '0cfe8dd171816a484b9def6cc27aec31'


class FlickrMediaContent(PreviewMediaService):
    def __init__(self):
        PreviewMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?flic.kr"
        self.xml_pattern = re.compile(r'''label="Original"\s
                                      width="(.*)"\s  # The width of the image
                                      height="(.*)"\s # The height of the image
                                      source="(.*)"\s # Image's source
                                      url="(.*)"\s    # The URL
                                      media="(.*)"''', re.VERBOSE)
        self.resp_pattern = re.compile('/photos/(.*)/(.*)/')

    def do_service(self, url):
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

        api_base = "http://api.flickr.com/services/rest"
        api_method = "/?method=flickr.photos.getSizes&api_key=%s&photo_id=%s"
        req_url = "".join([api_base, api_method]) % (API_KEY, photo_id)
        xml = self._get_content_from_url(req_url)
        resp = self.xml_pattern.search(xml)
        media_content_url = resp.groups(0)[2]
        rawimg = self._get_content_from_url(media_content_url)
        return Media.new_image(url, rawimg)
