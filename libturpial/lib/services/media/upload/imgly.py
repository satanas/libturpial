# -*- coding: utf-8 -*-

"""Img.ly service"""

from libturpial.exceptions import UploadImageError
from libturpial.lib.services.media.upload.base import UploadService


class ImglyUploader(UploadService):
    def __init__(self):
        UploadService.__init__(self, "img.ly", "/api/2/upload.xml")

    def do_service(self, account, filepath, message=None):
        files = {
            'media': open(filepath, 'rb'),
        }

        fields = {}
        if message:
            fields['message'] = message

        resp = self._upload_pic(account, fields, files)
        link = self._parse_xml('url', resp)
        if not link:
            raise UploadImageError
        return link
