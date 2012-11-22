# -*- coding: utf-8 -*-

"""Yfrog service"""
#
# Author: Wil Alvarez (aka Satanas)

import traceback

from libturpial.api.interfaces.service import ServiceResponse
from libturpial.api.services.uploadpic.base import UploadService

YFROG_KEY = '189ACHINb967317adad418caebd9a22615d00cb7'

class YfrogUploader(UploadService):
    def __init__(self):
        UploadService.__init__(self, "yfrog.com", "/api/xauth_upload",
            "https://api.twitter.com/1/account/verify_credentials.xml")

    def do_service(self, account, filepath, message):
        try:
            _image = self._open_file(filepath)
        except:
            return self._error_opening_file(filepath)

        files = (
            ('media', self._get_pic_name(filepath), _image),
        )

        fields = (
            ('key', YFROG_KEY),
        )
        try:
            resp = self._upload_pic(account, fields, files)
            link = self._parse_xml('mediaurl', resp)
            return ServiceResponse(link)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem uploading pic'))
