# -*- coding: utf-8 -*-

"""Lockers show media content service"""

from libturpial.api.models.media import Media
from libturpial.lib.services.media.preview.base import PreviewMediaService


class LockerzMediaContent(PreviewMediaService):
    def __init__(self):
        PreviewMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?lockerz.com"

    def do_service(self, url):
        api_base = 'http://api.plixi.com/api/tpapi.svc'
        api_method = '/imagefromurl?url=%s&size=big'
        url2 = "".join([api_base, api_method]) % url
        rawimg = self._get_content_from_url(url2)
        return Media.new_image(url, rawimg)
