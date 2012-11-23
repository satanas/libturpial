# -*- coding: utf-8 -*-

"""Imgur service"""
#
# Author: Wil Alvarez (aka Satanas)

import json
import base64
import urllib
import traceback

from libturpial.api.interfaces.service import ServiceResponse
from libturpial.api.services.uploadpic.base import UploadService

IMGUR_KEY = '710afc95df6a25864a9f7df6b6a0b103'


class ImgurUploader(UploadService):
    def __init__(self):
        UploadService.__init__(self, "api.imgur.com", "/2/upload.json",
            "https://api.twitter.com/1/account/verify_credentials.json")

    def do_service(self, account, filepath, message):
        try:
            _image = self._open_file(filepath)
        except:
            return self._error_opening_file(filepath)

        postdata = {"key": IMGUR_KEY,
            "image":base64.b64encode(_image),
            "caption":message}
        data = urllib.urlencode(postdata)

        try:
            fetch_url = "http://%s%s" % (self.host, self.base_url)
            resp = urllib.urlopen(fetch_url, data)
            resp_json = json.loads(resp.read())
            link = resp_json['upload']['links'].get('imgur_page')
            return ServiceResponse(link)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True,
                                   err_msg=_('Problem uploading pic'))
