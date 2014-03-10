# -*- coding: utf-8 -*-

""" pic.twitter.com show media content service """

from libturpial.api.models.media import Media
from libturpial.lib.services.media.preview.base import PreviewMediaService


class PicTwitterMediaContent(PreviewMediaService):
    def __init__(self):
        PreviewMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?(twimg.com|pic.twitter.com)"

    def do_service(self, url):
        info_ = {
            'source_url': url,
            'original_url': url,
        }
        rawimg = self._get_content_from_url(url)
        return Media.new_image(url, rawimg, info=info_)
