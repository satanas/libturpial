# -*- coding: utf-8 -*-

"""Generic module to handle HTTP request in Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

import os
import ssl
import sys
import socket
import urllib2
import logging
import requests

try:
    import oauth.oauth as oauth
except:
    import oauth


class TurpialHTTP:
    TIMEOUT = 20
    FORMAT_XML = 'xml'
    FORMAT_JSON = 'json'

    def __init__(self, base_url, username=None, password=None,
                 consumer_key=None, consumer_secret=None, user_key=None,
                 user_secret=None, verifier=None):
        self.base_url = base_url
        self.proxies = {}

        self.log = logging.getLogger('TurpialHTTP')

        # timeout in seconds
        socket.setdefaulttimeout(self.TIMEOUT)

        self.sign_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
        if  getattr(sys, 'frozen', None):
            basedir = sys._MEIPASS
            self.ca_certs_file = os.path.realpath(os.path.join(basedir,
                                                               'cacert.pem'))
        else:
            basedir = os.path.dirname(__file__)
            self.ca_certs_file = os.path.realpath(os.path.join(basedir,
                '..', '..', 'certs', 'cacert.pem'))

        if consumer_key and consumer_secret and user_key and user_secret and verifier:
            self.setup_for_oauth(consumer_key, consumer_secret, user_key, user_secret, verifier)
        elif username and password:
            self.setup_for_basic_auth(username, password)

    def __sign_request_for_oauth(self, httpreq):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                                                             token=self.token,
                                                             http_method=httpreq.method,
                                                             http_url=httpreq.uri,
                                                             parameters=httpreq.params)
        request.sign_request(self.sign_method_hmac_sha1,
                             self.consumer, self.token)
        httpreq.headers.update(request.to_header())

    def __sign_request_for_basic_auth(self, httpreq):
        auth_info = b64encode("%s:%s" % (self.username, self.password))
        httpreq.headers["Authorization"] = ''.join(["Basic ", auth_info])

    def __validate_ssl_cert(self, request):
        req = request.split('://')[1]
        host = req[:req.find('/')]
        port = 443

        ip = socket.getaddrinfo(host, port)[0][4][0]
        sock = socket.socket()
        sock.connect((ip, port))

        sock = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_REQUIRED,
                               ca_certs=self.ca_certs_file)

        cert = sock.getpeercert()

        for field in cert['subject']:
            if field[0][0] == 'commonName':
                certhost = field[0][1]
                if certhost != host:
                    raise ssl.SSLError("Host name '%s' doesn't match certificate host '%s'" % (host, certhost))

        self.log.debug('Validated SSL cert for host: %s' % host)

    def setup_for_oauth(self, consumer_key, consumer_secret, user_key, user_secret, verifier):
        self.token = oauth.OAuthToken(user_key, user_secret)
        self.token.set_verifier(verifier)
        self.consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)

    def setup_for_basic_auth(self, username, password):
        self.token = None
        self.consumer = None
        self.username = username
        self.password = password

    # ------------------------------------------------------------
    # OAuth Methods
    # ------------------------------------------------------------

    def request_token(self):
        self.log.debug('Obtain a request token')
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                                                                   http_url=self.REQUEST_TOKEN_URL)

        oauth_request.sign_request(self.sign_method_hmac_sha1,
                                   self.consumer, None)

        #self.log.debug('REQUEST (via headers)')
        #self.log.debug('parameters: %s' % str(oauth_request.parameters))

        req = urllib2.Request(self.REQUEST_TOKEN_URL,
                              headers=oauth_request.to_header())
        response = urllib2.urlopen(req)
        self.token = oauth.OAuthToken.from_string(response.read())
        #self.log.debug('GOT')
        #self.log.debug('key: %s' % str(self.token.key))
        #self.log.debug('secret: %s' % str(self.token.secret))
        #self.log.debug('callback confirmed? %s' % str(self.token.callback_confirmed))

        self.log.debug('Authorize the request token')
        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=self.token,
                                                                   http_url=self.AUTHORIZATION_URL)

        #self.log.debug('REQUEST (via url query string)')
        #self.log.debug('parameters: %s' % str(oauth_request.parameters))
        return oauth_request.to_url()

    def authorize_token(self, pin):
        self.log.debug('Obtain an access token')
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                                                                   token=self.token,
                                                                   verifier=pin,
                                                                   http_url=self.ACCESS_TOKEN_URL)

        oauth_request.sign_request(self.sign_method_hmac_sha1,
                                   self.consumer, self.token)

        self.log.debug('REQUEST (via headers)')
        self.log.debug('parameters: %s' % str(oauth_request.parameters))

        req = urllib2.Request(self.ACCESS_TOKEN_URL,
                              headers=oauth_request.to_header())
        response = urllib2.urlopen(req)
        self.token = oauth.OAuthToken.from_string(response.read())

        self.log.debug('GOT')
        self.log.debug('key: %s' % str(self.token.key))
        self.log.debug('secret: %s' % str(self.token.secret))
        self.token.verifier = pin
        return self.token

    '''
    def __fetch_xauth_access_token(self, username, password):
        request = oauth.OAuthRequest.from_consumer_and_token(
            oauth_consumer=self.consumer,
            http_method='POST', http_url=self.access_url,
            parameters = {
                'x_auth_mode': 'client_auth',
                'x_auth_username': username,
                'x_auth_password': password
            }
        )
        request.sign_request(self.sign_method_hmac_sha1, self.consumer, None)

        req = urllib2.Request(self.access_url, data=request.to_postdata())
        response = urllib2.urlopen(req)
        self.token = oauth.OAuthToken.from_string(response.read())
        self.auth_args['key'] = self.token.key
        self.auth_args['secret'] = self.token.secret
    '''

    # ------------------------------------------------------------
    # Main Methods
    # ------------------------------------------------------------

    def set_proxy(self, host, port, username='', password='', https=False):
        proxy_auth = ''
        if username and password:
            proxy_auth = "%s:%s@" % (username, password)

        protocol = 'https' if https else 'http'
        self.proxies[protocol] = "%s://%s%s:%s" % (protocol, proxy_auth, host, port)

    def build_request(self, method, uri, args, _format, secure):
        if 'id' in args:
            uri = "%s/%s" % (uri, args['id'])
            del args['id']

        if _format is None:
            uri = "%s" % (uri)
        else:
            uri = "%s.%s" % (uri, _format)

        return TurpialHTTPRequest(method, uri, params=args, secure=secure)

    def auth_request(self, httpreq):
        if self.token:
            self.__sign_request_for_oauth(httpreq)
        else:
            self.__sign_request_for_basic_auth(httpreq)

    def fetch_resource(self, httpreq):
        if httpreq.method == 'GET':
            req = requests.get(httpreq.uri, params=httpreq.params,
                    headers=httpreq.headers, verify=httpreq.secure,
                    proxies=self.proxies)
        elif httpreq.method == 'POST':
            req = requests.post(httpreq.uri, params=httpreq.params,
                    headers=httpreq.headers, verify=httpreq.secure,
                    proxies=self.proxies)

        print req.url
        if httpreq._format == self.FORMAT_JSON:
            return req.json()
        else:
            return req.text

    def get(self, uri, args=None, _format=FORMAT_JSON, base_url=None, secure=False):
        self.request('GET', uri, args, _format, base_url, secure)

    def post(self, uri, args=None, _format=FORMAT_JSON, base_url=None, secure=False):
        self.request('POST', uri, args, _format, base_url, secure)

    def request(self, method, uri, args=None, _format=FORMAT_JSON,
            base_url=None, secure=False):
        if args is None:
            args = {}
        if not base_url:
            base_url = self.base_url
        if secure:
            base_url = base_url.replace('http://', 'https://')
            self.__validate_ssl_cert(base_url)

        request_url = "%s%s" % (base_url, uri)

        httpreq = self.build_request(method, request_url, args, _format, secure)
        self.auth_request(httpreq)
        return self.fetch_resource(httpreq)


class TurpialHTTPRequest:
    def __init__(self, method, uri, headers=None, params=None,
            _format=TurpialHTTP.FORMAT_JSON, secure=False):

        self.uri = uri
        self.method = method
        self._format = _format
        self.secure = secure
        self.params = params if params is not None else {}
        self.headers = headers if headers is not None else {}
