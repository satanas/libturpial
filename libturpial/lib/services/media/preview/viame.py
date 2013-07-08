# -*- coding: utf-8 -*-

"""Via.me show media content service"""

import json

from libturpial.api.models.media import Media
from libturpial.lib.services.media.preview.base import PreviewMediaService

CLIENT_ID = '3ycgz7gzer80068s80t4xl1cs'


class ViameMediaContent(PreviewMediaService):
    def __init__(self):
        PreviewMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?via.me"

    def do_service(self, url):
        post_id = url.split('/')[-1][1:]
        req_url = 'https://api.via.me/v1/posts/%s?client_id=%s' % (post_id,
                                                                   CLIENT_ID)
        resp = json.loads(self._get_content_from_url(req_url))
        media_content_url = resp['response']['post']['media_url']
        rawimg = self._get_content_from_url(media_content_url)
        return Media.new_image(url, rawimg)
