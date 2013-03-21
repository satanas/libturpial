# -*- coding: utf-8 -*-

"""Generic module to handle HTTP request in Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

import os
import ssl
import sys
import socket
import urllib
import urllib2
import httplib
import logging

from base64 import b64encode
from urllib import urlencode

from libturpial.api.models.auth_object import AuthObject


def _py26_or_greater():
    return sys.hexversion > 0x20600f0

try:
    import oauth.oauth as oauth
except:
    import oauth

try:
    import json
except ImportError:
    import simplejson as json


class TurpialHTTP:
    DEFAULT_FORMAT = 'json'
    TIMEOUT = 20

    def __init__(self, base_url, username=None, password=None,
                 consumer_key=None, consumer_secret=None, user_key=None,
                 user_secret=None, verifier=None):
        self.base_url = base_url

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

    def __oauth_sign_http_request(self, httpreq):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                                                             token=self.token,
                                                             http_method=httpreq.method,
                                                             http_url=httpreq.uri,
                                                             parameters=httpreq.params)
        request.sign_request(self.sign_method_hmac_sha1,
                             self.consumer, self.token)
        httpreq.headers.update(request.to_header())

    def __basic_sign_http_request(self, httpreq):
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
    # Common Methods
    # ------------------------------------------------------------

    def start_login(self, account_id):
        if self.oauth_support:
            return self.start_oauth(account_id)
        else:
            return AuthObject('basic', account_id, token=None)

    def set_proxy(self, proxy):
        self.log.debug('Proxies detected: %s' % proxy)
        proxy_url = {}

        if proxy.secure:
            proxy_url['https'] = "%s:%d" % (proxy.server, proxy.port)
        else:
            proxy_url['http'] = "%s:%d" % (proxy.server, proxy.port)

        if _py26_or_greater():
            opener = urllib2.build_opener(urllib2.ProxyHandler(proxy_url),
                                          urllib2.HTTPHandler)
        else:
            opener = urllib2.build_opener(ConnectHTTPSHandler(proxy=proxy_url))
        urllib2.install_opener(opener)

    def build_http_request(self, uri, method, args, _format):
        '''Construir la petición HTTP'''
        argStr = ''
        headers = {}
        argData = None
        encoded_args = ''

        if 'id' in args:
            uri = "%s/%s" % (uri, args['id'])
            del args['id']

        if _format is None:
            uri = "%s" % (uri)
        else:
            uri = "%s.%s" % (uri, _format)

        if len(args) > 0:
            s_args = []
            for k, v in args.items():
                s_args.append((k, v))
            encoded_args = urlencode(s_args)


        if method == "GET":
            if encoded_args:
                argStr = "?%s" % (encoded_args)
        else:
            argData = encoded_args

        strReq = "%s%s" % (uri, argStr)

        if method == "GET":
            self.log.debug('GET %s' % strReq)
        else:
            self.log.debug('POST %s with params: %s' % (uri, argData))

        req = TurpialHTTPRequest(argStr, headers, argData, encoded_args,
                                 method, strReq, uri, args)
        #print req
        return req

    def auth_http_request(self, httpreq):
        if self.token:
            self.__oauth_sign_http_request(httpreq)
        else:
            self.__basic_sign_http_request(httpreq)

    def fetch_http_resource(self, httpreq, _format, redirect):
        print httpreq.strReq, httpreq.argData, httpreq.headers
        req = urllib2.Request(httpreq.strReq, httpreq.argData, httpreq.headers)
        handle = None
        if redirect:
            opener = urllib2.build_opener(RedirectHandler())
            handle = opener.open(req)
        else:
            handle = urllib2.urlopen(req)
        response = handle.read()
        if _format == 'json':
            return json.loads(response)
        else:
            return response

    def request(self, url, method='GET', args=None, _format=DEFAULT_FORMAT, base_url=None,
                secure=False, redirect=False):
        if args is None:
            args = {}
        if not base_url:
            base_url = self.base_url
        if secure:
            base_url = base_url.replace('http://', 'https://')
            self.__validate_ssl_cert(base_url)

        request_url = "%s%s" % (base_url, url)
        httpreq = self.build_http_request(request_url, method, args, _format)
        print httpreq.headers
        self.auth_http_request(httpreq)
        print httpreq.headers
        return self.fetch_http_resource(httpreq, _format, redirect)


class TurpialHTTPRequest:
    def __init__(self, argStr='', headers=None, argData=None, encoded_args='',
                 method="GET", strReq='', uri='', params=None):

        self.argStr = argStr
        self.headers = headers if headers is not None else {}
        self.argData = argData
        self.encoded_args = encoded_args
        self.method = method
        self.strReq = strReq
        self.params = params if params is not None else {}
        self.uri = uri

    def __str__(self):
        return " method: %s\n encoded_args: %s\n argStr: %s\n argData: %s\n \
headers: %s\n strReq: %s\n***" % (self.method, self.encoded_args,
                                  self.argStr, self.argData,
                                  self.headers, self.strReq)


class ProxyHTTPConnection(httplib.HTTPConnection):

    _ports = {'http': 80, 'https': 443}

    def request(self, method, url, body=None, headers=None):
        #request is called before connect, so can interpret url and get
        #real host/port to be used to make CONNECT request to proxy
        if headers is None:
            headers = {}
        proto, rest = urllib.splittype(url)
        if proto is None:
            raise ValueError("unknown URL type: %s" % url)
        #get host
        host, rest = urllib.splithost(rest)
        #try to get port
        host, port = urllib.splitport(host)
        #if port is not defined try to get from proto
        if port is None:
            try:
                port = self._ports[proto]
            except KeyError:
                raise ValueError("unknown protocol for: %s" % url)
        self._real_host = host
        self._real_port = port
        httplib.HTTPConnection.request(self, method, url, body, headers)

    def connect(self):
        httplib.HTTPConnection.connect(self)
        #send proxy CONNECT request
        self.send("CONNECT %s:%d HTTP/1.0\r\n\r\n" % (self._real_host,
                                                      self._real_port))
        #expect a HTTP/1.0 200 Connection established
        response = self.response_class(self.sock, strict=self.strict,
                                       method=self._method)
        (_, code, message) = response._read_status()
        #probably here we can handle auth requests...
        if code != 200:
            #proxy returned and error, abort connection, and raise exception
            self.close()
            raise socket.error("Proxy connection failed: %d %s" %
                               (code, message.strip()))
        #eat up header block from proxy....
        while True:
            #should not use directly fp probablu
            line = response.fp.readline()
            if line == '\r\n':
                break


class ProxyHTTPSConnection(ProxyHTTPConnection):

    default_port = 443

    def __init__(self, host, port=None, key_file=None,
                 cert_file=None, strict=None):
        ProxyHTTPConnection.__init__(self, host, port)
        self.key_file = key_file
        self.cert_file = cert_file

    def connect(self):
        ProxyHTTPConnection.connect(self)
        #make the sock ssl-aware
        _ssl = socket.ssl(self.sock, self.key_file, self.cert_file)
        self.sock = httplib.FakeSocket(self.sock, _ssl)


class ConnectHTTPHandler(urllib2.HTTPHandler):

    def __init__(self, proxy=None, debuglevel=0):
        self.proxy = proxy
        urllib2.HTTPHandler.__init__(self, debuglevel)

    def do_open(self, http_class, req):
        if self.proxy is not None:
            req.set_proxy(self.proxy, 'http')
        return urllib2.HTTPHandler.do_open(self, ProxyHTTPConnection, req)


class ConnectHTTPSHandler(urllib2.HTTPSHandler):

    def __init__(self, proxy=None, debuglevel=0):
        self.proxy = proxy
        urllib2.HTTPSHandler.__init__(self, debuglevel)

    def do_open(self, http_class, req):
        if self.proxy is not None:
            req.set_proxy(self.proxy, 'https')
        return urllib2.HTTPSHandler.do_open(self, ProxyHTTPSConnection, req)


class RedirectHandler(urllib2.HTTPRedirectHandler):
    def __handle_redirect(self, url):
        req = urllib2.Request(url)
        handle = urllib2.urlopen(req)
        return handle

    def http_error_301(self, req, fp, code, msg, headers):
        #print headers['Location']
        return self.__handle_redirect(headers['Location'])

    def http_error_302(self, req, fp, code, msg, headers):
        #print headers['Location']
        return self.__handle_redirect(headers['Location'])
