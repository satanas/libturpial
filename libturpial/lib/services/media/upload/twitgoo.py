# -*- coding: utf-8 -*-

"""Twitgoo service"""

from libturpial.exceptions import UploadImageError
from libturpial.lib.services.media.upload.base import UploadService


class TwitgooUploader(UploadService):
    def __init__(self):
        UploadService.__init__(self, "twitgoo.com", "/api/upload")

    def do_service(self, account, filepath, message):
        files = {
            'media': open(filepath, 'rb'),
        }

        fields = {
            'message': message or '',
        }

        resp = self._upload_pic(account, fields, files)
        link = self._parse_xml('mediaurl', resp)
        if not link:
            raise UploadImageError
        return link
