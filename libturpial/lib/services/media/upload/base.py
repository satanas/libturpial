# -*- coding: utf-8 -*-

"""Common interface for upload media services"""

import os
import requests

from libturpial.lib.http import TurpialHTTPRequest
from libturpial.lib.interfaces.service import GenericService


class UploadService(GenericService):
    def __init__(self, host, base_url):
        self.host = host
        self.base_url = base_url
        self.end_point = "http://%s%s" % (host, base_url)

    def _upload_pic(self, account, fields, files, custom_headers=None):
        """
        Post fields and files to an http host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be
            uploaded as files
        Return the server's response page.
        """

        httpreq = TurpialHTTPRequest(method='GET', uri=account.verify_credentials_provider())
        account.protocol.http.sign_request(httpreq)

        headers = httpreq.headers
        headers['User-Agent'] = 'Turpial'
        headers['X-Auth-Service-Provider'] = account.verify_credentials_provider()
        auth_headers = httpreq.headers['Authorization']
        auth_headers = auth_headers.replace('OAuth realm=""', 'OAuth realm="http://api.twitter.com/"')
        headers['X-Verify-Credentials-Authorization'] = auth_headers
        if custom_headers:
            headers = dict(headers.items() + custom_headers.items())

        r = requests.post(self.end_point, files=files, data=fields, headers=headers)
        return r.text
