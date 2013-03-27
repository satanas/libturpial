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

DEFAULT_TIMEOUT = 20
FORMAT_XML = 'xml'
FORMAT_JSON = 'json'


class TurpialHTTPGeneric:
    """TurpialHTTP is abstraction of the HTTP protocol for libturpial. It handles all the http
    requests, taking care of the OAuth/Basic authentication, SSL and all that
    stuff.

    First parameter is the base URL of the service, for example: 
    http://api.twitter.com/1. Then according the type of request you need to
    specify the other. TurpialHTTP supports two modes:

    * OAuth: For this method you must set the **consumer_key** and 
    the **consumer_secret** (those values are given by Twitter for your app), 
    the **user_key**, **user_secret** and **verifier** (a.k.a pin). The user
    variables are get after the *OAuth dance*.
    """

    def __init__(self, base_url, proxies=None, timeout=None):
        self.base_url = base_url
        self.proxies = proxies or {}
        self.timeout = timeout or DEFAULT_TIMEOUT

        self.log = logging.getLogger('TurpialHTTP')

        if getattr(sys, 'frozen', None):
            basedir = sys._MEIPASS
            self.ca_certs_file = os.path.realpath(os.path.join(basedir,
                                                               'cacert.pem'))
        else:
            basedir = os.path.dirname(__file__)
            self.ca_certs_file = os.path.realpath(os.path.join(basedir,
                '..', '..', 'certs', 'cacert.pem'))

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

    def __build_request(self, method, uri, args, _format, secure):
        if 'id' in args:
            uri = "%s/%s" % (uri, args['id'])
            del args['id']

        if _format is None:
            uri = "%s" % (uri)
        else:
            uri = "%s.%s" % (uri, _format)

        return TurpialHTTPRequest(method, uri, params=args, secure=secure)

    def __auth_request(self, httpreq):
        self._sign_request(httpreq)

    def __fetch_resource(self, httpreq):
        if httpreq.method == 'GET':
            req = requests.get(httpreq.uri, params=httpreq.params,
                    headers=httpreq.headers, verify=httpreq.secure,
                    proxies=self.proxies, timeout=self.timeout)
        elif httpreq.method == 'POST':
            req = requests.post(httpreq.uri, params=httpreq.params,
                    headers=httpreq.headers, verify=httpreq.secure,
                    proxies=self.proxies, timeout=self.timeout)

        print req.url
        if httpreq._format == FORMAT_JSON:
            return req.json()
        else:
            return req.text

    def _sign_request(self, httpreq):
        raise NotImplementedError

    # ------------------------------------------------------------
    # OAuth Methods
    # -----------------------------------------------------------

    # ------------------------------------------------------------
    # Main Methods
    # ------------------------------------------------------------

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_proxy(self, host, port, username='', password='', https=False):
        proxy_auth = ''
        if username and password:
            proxy_auth = "%s:%s@" % (username, password)

        protocol = 'https' if https else 'http'
        self.proxies[protocol] = "%s://%s%s:%s" % (protocol, proxy_auth, host, port)

    def get(self, uri, args=None, _format=FORMAT_JSON, base_url=None, secure=False):
        self.request('GET', uri, args, _format, base_url, secure)

    def post(self, uri, args=None, _format=FORMAT_JSON, base_url=None, secure=False):
        self.request('POST', uri, args, _format, base_url, secure)

    def request(self, method, uri, args=None, _format=FORMAT_JSON,
            alt_base_url=None, secure=False):

        args = args or {}
        base_url = alt_base_url or self.base_url

        if secure:
            base_url = base_url.replace('http://', 'https://')
            self.__validate_ssl_cert(base_url)

        request_url = "%s%s" % (base_url, uri)

        httpreq = self.__build_request(method, request_url, args, _format, secure)
        self.__auth_request(httpreq)
        return self.__fetch_resource(httpreq)


class TurpialHTTPOAuth(TurpialHTTPGeneric):
    """
    oauth_options = {
        'consumer_key'
        'consumer_secret'
        'request_token_url'
        'authorize_token_url'
        'access_token_url'
    }
    """
    def __init__(self, base_url, oauth_options, user_key=None, user_secret=None,
            verifier=None, proxies=None, timeout=None):
        TurpialHTTPGeneric.__init__(self, base_url, proxies, timeout)

        self.request_token_url = oauth_options['request_token_url']
        self.authorize_token_url = oauth_options['authorize_token_url']
        self.access_token_url = oauth_options['access_token_url']

        self.consumer = oauth.OAuthConsumer(oauth_options['consumer_key'],
                oauth_options['consumer_secret'])
        self.sign_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

        if user_key and user_secret and verifier:
            self.token = oauth.OAuthToken(user_key, user_secret)
            self.token.set_verifier(verifier)
        else:
            self.token = None

    def _sign_request(self, httpreq):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                token=self.token, http_method=httpreq.method,
                http_url=httpreq.uri, parameters=httpreq.params)

        request.sign_request(self.sign_method_hmac_sha1, self.consumer,
                self.token)
        httpreq.headers.update(request.to_header())

    def set_user_info(self, user_key, user_secret, verifier):
        self.token = oauth.OAuthToken(user_key, user_secret)
        self.token.set_verifier(verifier)

    def request_token(self):
        self.log.debug('Obtain a request token')
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                http_url=self.request_token_url)

        oauth_request.sign_request(self.sign_method_hmac_sha1, self.consumer, None)

        #self.log.debug('REQUEST (via headers)')
        #self.log.debug('parameters: %s' % str(oauth_request.parameters))

        req = urllib2.Request(self.request_token_url, headers=oauth_request.to_header())
        response = urllib2.urlopen(req)
        self.token = oauth.OAuthToken.from_string(response.read())
        #self.log.debug('GOT')
        #self.log.debug('key: %s' % str(self.token.key))
        #self.log.debug('secret: %s' % str(self.token.secret))
        #self.log.debug('callback confirmed? %s' % str(self.token.callback_confirmed))

        self.log.debug('Authorize the request token')
        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=self.token,
                http_url=self.authorization_token_url)

        #self.log.debug('REQUEST (via url query string)')
        #self.log.debug('parameters: %s' % str(oauth_request.parameters))
        return oauth_request.to_url()

    def authorize_token(self, pin):
        self.log.debug('Obtain an access token')
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                token=self.token, verifier=pin, http_url=self.access_token_url)

        oauth_request.sign_request(self.sign_method_hmac_sha1, self.consumer,
                self.token)

        self.log.debug('REQUEST (via headers)')
        self.log.debug('parameters: %s' % str(oauth_request.parameters))

        req = urllib2.Request(self.access_token_url, headers=oauth_request.to_header())
        response = urllib2.urlopen(req)
        self.token = oauth.OAuthToken.from_string(response.read())

        self.log.debug('GOT')
        self.log.debug('key: %s' % str(self.token.key))
        self.log.debug('secret: %s' % str(self.token.secret))
        self.token.verifier = pin
        return self.token

    def fetch_xauth_access_token(self, username, password):
        request = oauth.OAuthRequest.from_consumer_and_token(
            oauth_consumer=self.consumer,
            http_method='POST', http_url=self.access_token_url,
            parameters = {
                'x_auth_mode': 'client_auth',
                'x_auth_username': username,
                'x_auth_password': password
            }
        )
        request.sign_request(self.sign_method_hmac_sha1, self.consumer, None)

        req = urllib2.Request(self.access_token_url, data=request.to_postdata())
        response = urllib2.urlopen(req)
        self.token = oauth.OAuthToken.from_string(response.read())


class TurpialHTTPBasicAuth(TurpialHTTPGeneric):
    def __init__(self, base_url, username, password, proxies=None, timeout=None):
        TurpialHTTPGeneric.__init__(self, base_url, proxies, timeout)

        auth_info = b64encode("%s:%s" % (username, password))
        self.basic_auth_info = ''.join(["Basic ", auth_info])

    def _sign_request(self, httpreq):
        httpreq.headers["Authorization"] = self.basic_auth_info



class TurpialHTTPRequest:
    def __init__(self, method, uri, headers=None, params=None,
            _format=FORMAT_JSON, secure=False):

        self.uri = uri
        self.method = method
        self._format = _format
        self.secure = secure
        self.params = params or {}
        self.headers = headers or {}
