# -*- coding: utf-8 -*-

"""Mobypicture service"""

from libturpial.exceptions import UploadImageError
from libturpial.lib.services.media.upload.base import UploadService

MOBYPICTURE_KEY = 'uF6kIJuyGGKsol8i'


class MobypictureUploader(UploadService):
    def __init__(self):
        UploadService.__init__(self, "api.mobypicture.com", "/2.0/upload.xml")

    def do_service(self, account, filepath, message=None):
        files = {
            'media': open(filepath, 'rb'),
        }

        fields = {
            'key': MOBYPICTURE_KEY,
            'message': message or '',
        }
        resp = self._upload_pic(account, fields, files)
        link = self._parse_xml('mediaurl', resp)
        if not link:
            raise UploadImageError
        return link
