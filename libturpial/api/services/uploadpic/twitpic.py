# -*- coding: utf-8 -*-

"""Twitpic service"""
#
# Author: Wil Alvarez (aka Satanas)
# 2010-04-19

import traceback
from picservice import *

TWITPIC_KEY = '57d17b42f1001ffc64bf22ceef98968d'


class TwitpicPicUploader(PicService):
    def __init__(self):
        PicService.__init__(self, "api.twitpic.com", "/2/upload.xml",
            "https://api.twitter.com/1/account/verify_credentials.json")

    def do_service(self, account, filepath, message):
        try:
            _image = self._open_file(filepath)
        except:
            return self._error_opening_file(filepath)

        files = (
            ('media', self._get_pic_name(filepath), _image),
        )

        fields = (
            ('key', TWITPIC_KEY),
            ('message', message),
        )
        try:
            resp = self._upload_pic(account, fields, files)
            print resp
            link = self._parse_xml('url', resp)
            return ServiceResponse(link)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True,
                                   err_msg=_('Problem uploading pic'))
