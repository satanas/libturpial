# -*- coding: utf-8 -*-

""" Instagram show media content service """

try:
    import simplejson as json
except:
    import json

from libturpial.api.models.media import *
from libturpial.lib.services.media.preview.base import *

CLIENT_ID = '3d1904e17ee745e49435bd6b27431af3'


class InstagramMediaContent(PreviewMediaService):
    def __init__(self):
        PreviewMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?instagram.com"

    def do_service(self, url):
        media_url = 'https://api.instagram.com/oembed?url=%s' % url
        rtn = json.loads(self._get_content_from_url(media_url))
        media_id = rtn['media_id']
        req_url = 'https://api.instagram.com/v1/media/%s?client_id=%s' % (media_id, CLIENT_ID)
        response = json.loads(self._get_content_from_url(req_url))
        image_url = response['data']['images']['standard_resolution']['url']
        info_ = {
            'source_url': image_url,
            'original_url': url,
        }
        rawimg = self._get_content_from_url(image_url)
        return Media.new_image(url, rawimg, info=info_)
