# -*- coding: utf-8 -*-

"""Lockerz service"""
#
# Author: Wil Alvarez (aka Satanas)

import httplib
import urlparse
import traceback
import mimetypes

from libturpial.api.interfaces.http import TurpialHTTPRequest
from libturpial.api.interfaces.service import ServiceResponse
from libturpial.api.services.uploadpic.base import UploadService

LOCKERZ_KEY = '09e874f8-a7ed-4ae4-a810-3cf7040b9c40'


class LockerzUploader(UploadService):
    def __init__(self):
        UploadService.__init__(self, "api.plixi.com", "/api/tpapi.svc/upload2",
            "https://api.twitter.com/1/account/verify_credentials.json")

    def _upload_pic(self, account, filepath, message, _image):
        BLOCKSIZE = 8192

        content_type = mimetypes.guess_type(filepath)[0] or 'image/jpg'

        headers = {
            'User-Agent': 'Turpial',
            'TPSERVICE': 'Plixi',
            'TPAPIKEY': LOCKERZ_KEY,
            'TPMIMETYPE': content_type,
        }

        if message != '':
            headers['TPMSG'] = message

        httpreq = TurpialHTTPRequest(method='GET', uri=self.provider)
        httpresp = account.auth_http_request(httpreq, {})
        auth_head = httpresp.headers['Authorization']
        auth_head = auth_head.replace('OAuth realm=""',
                                      'OAuth realm="http://api.twitter.com/"')

        headers['X-Verify-Credentials-Authorization'] = auth_head
        headers['X-Auth-Service-Provider'] = self.provider
        headers['content-type'] = 'application/x-www-form-urlencoded'
        headers['content-length'] = str(len(_image))

        url = "http://%s%s" % (self.host, self.base_url)
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)

        h = httplib.HTTP(netloc)
        h.putrequest('POST', '/%s' % path)

        for k, v in headers.items():
            if v is not None:
                h.putheader(k, v)
        h.endheaders()

        offset = 0
        for i in range(0, len(_image), BLOCKSIZE):
            offset += BLOCKSIZE
            h.send(_image[i: offset])

        code, msg, _x = h.getreply()
        return h.file.read()

    def do_service(self, account, filepath, message):
        try:
            _image = self._open_file(filepath)
        except:
            return self._error_opening_file(filepath)

        try:
            resp = self._upload_pic(account, filepath, message, _image)
            if 'Error' in resp:
                raise Exception, 'Error posting to lockerz'
            link = self._parse_xml('MediaUrl', resp)
            return ServiceResponse(link)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True,
                                   err_msg='Problem uploading pic')
