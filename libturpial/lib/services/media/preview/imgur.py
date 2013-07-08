# -*- coding: utf-8 -*-

"""Imgur show media content service"""

import json

from libturpial.api.models.media import Media
from libturpial.lib.services.media.preview.base import PreviewMediaService

API_KEY = '7ea1d30de2992c783a567df86faa388e'


class ImgurMediaContent(PreviewMediaService):
    def __init__(self):
        PreviewMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?imgur.com"

    def do_service(self, url):
        img_id = url.split('/')[-1].split('.')[0]
        req_url = 'https://api.imgur.com/2/image/%s.json' % (img_id)
        resp = json.loads(self._get_content_from_url(req_url))
        media_content_url = resp['image']['links']['original']
        rawimg = self._get_content_from_url(media_content_url)
        return Media.new_image(url, rawimg)

    def __find_url_in_html(self, html):
        path = '<link rel="image_src" href="'
        start = html.find(path) + len(path)
        end = html.find('" />', start, len(html))
        return html[start:end], html[start:end].split('/')[-1]
