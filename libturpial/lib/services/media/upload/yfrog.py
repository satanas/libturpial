# -*- coding: utf-8 -*-

"""Yfrog service"""

from libturpial.exceptions import UploadImageError
from libturpial.lib.services.media.upload.base import UploadService

YFROG_KEY = '189ACHINb967317adad418caebd9a22615d00cb7'


class YfrogUploader(UploadService):
    def __init__(self):
        UploadService.__init__(self, "yfrog.com", "/api/xauth_upload")

    def do_service(self, account, filepath, message=None):
        files = {
            'media': open(filepath, 'rb'),
        }

        fields = {
            'key': YFROG_KEY,
        }

        resp = self._upload_pic(account, fields, files)
        if resp.find('fail') > 0 and resp.find('err code') > 0:
            raise UploadImageError

        link = self._parse_xml('mediaurl', resp)
        if not link:
            raise UploadImageError
        return link
