# -*- coding: utf-8 -*-

"""Twitpic service"""

from libturpial.exceptions import UploadImageError
from libturpial.lib.services.media.upload.base import UploadService

TWITPIC_KEY = '57d17b42f1001ffc64bf22ceef98968d'


class TwitpicUploader(UploadService):
    def __init__(self):
        UploadService.__init__(self, "api.twitpic.com", "/2/upload.xml")

    def do_service(self, account, filepath, message=None):
        files = {
            'media': open(filepath, 'rb'),
        }

        fields = {
            'key': TWITPIC_KEY,
            'message': message or '',
        }
        resp = self._upload_pic(account, fields, files)
        link = self._parse_xml('url', resp)
        if not link:
            raise UploadImageError
        return link
