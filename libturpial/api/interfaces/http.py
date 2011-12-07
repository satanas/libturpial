# -*- coding: utf-8 -*-

"""Generic module to handle HTTP request in Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

import socket
import urllib2
import urllib
import httplib
import logging

from base64 import b64encode
from urllib import urlencode

from libturpial.api.protocols import oauth
from libturpial.api.models.auth_object import AuthObject

def _py26_or_greater():
    import sys
    return sys.hexversion > 0x20600f0

try:
    import json
except ImportError:
    import simplejson as json

class TurpialHTTP:
    DEFAULT_FORMAT = 'json'
    
    def __init__(self, post_actions, oauth_support=True):
        self.urls = {}
        self.auth_args = {'key':'', 'secret':'', 'verifier':''}
        self.post_actions = post_actions
        self.log = logging.getLogger('TurpialHTTP')
        # timeout in seconds
        timeout = 20
        socket.setdefaulttimeout(timeout)
        self.oauth_support = oauth_support
        self.token = None
        self.consumer = None
        self.sign_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
        
    def __oauth_sign_http_request(self, httpreq, args):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
            token=self.token, http_method=httpreq.method, http_url=httpreq.uri,
            parameters=httpreq.params)
        request.sign_request(self.sign_method_hmac_sha1,
            self.consumer, self.token)
        httpreq.headers.update(request.to_header())
        return httpreq
    
    def __basic_sign_http_request(self, httpreq, args):
        username = args['username']
        password = args['password']
        if username:
            auth_info = b64encode("%s:%s" % (username, password))
            httpreq.headers["Authorization"] = "Basic " + auth_info
        return httpreq
    
    # ------------------------------------------------------------
    # OAuth Methods
    # ------------------------------------------------------------
    
    def set_auth_info(self, auth):
        self.auth_args = auth
        
    def set_consumer(self, key, sec):
        self.consumer = oauth.OAuthConsumer(key, sec)
        
    def start_oauth(self, account_id):
        if self.auth_args['key'] != '' and self.auth_args['secret'] != '' and \
        self.auth_args['verifier'] != '':
            token = self.build_token(self.auth_args)
            return AuthObject('done', account_id, token=token)
        else:
            url = self.request_token()
            return AuthObject('auth', account_id, url=url)
    
    def build_token(self, auth):
        self.token = oauth.OAuthToken(auth['key'], auth['secret'])
        self.token.set_verifier(auth['verifier'])
        return self.token
        
    def request_token(self):
        self.log.debug('Obtain a request token')
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
            http_url=self.REQUEST_TOKEN_URL)
        
        oauth_request.sign_request(self.sign_method_hmac_sha1,
            self.consumer, None)
        
        self.log.debug('REQUEST (via headers)')
        self.log.debug('parameters: %s' % str(oauth_request.parameters))
        
        req = urllib2.Request(self.REQUEST_TOKEN_URL, headers=oauth_request.to_header())
        response = urllib2.urlopen(req)
        self.token = oauth.OAuthToken.from_string(response.read())
        
        self.log.debug('GOT')
        self.log.debug('key: %s' % str(self.token.key))
        self.log.debug('secret: %s' % str(self.token.secret))
        self.log.debug('callback confirmed? %s' % str(self.token.callback_confirmed))
        
        self.log.debug('Authorize the request token')
        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=self.token,
            http_url=self.AUTHORIZATION_URL)
        
        self.log.debug('REQUEST (via url query string)')
        self.log.debug('parameters: %s' % str(oauth_request.parameters))
        return oauth_request.to_url()
        
    def authorize_token(self, pin):
        self.log.debug('Obtain an access token')
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
            token=self.token, verifier=pin,
            http_url=self.ACCESS_TOKEN_URL)
        
        oauth_request.sign_request(self.sign_method_hmac_sha1,
            self.consumer, self.token)
        
        self.log.debug('REQUEST (via headers)')
        self.log.debug('parameters: %s' % str(oauth_request.parameters))
        
        req = urllib2.Request(self.ACCESS_TOKEN_URL, headers=oauth_request.to_header())
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
        self.log.debug('Proxies detected: %s' % proxies)
        proxy_url = {}
        
        if proxy.secure:
            proxy_url['https'] = "%s:%d" % (proxy.server, proxy.port)
        else:
            proxy_url['http'] = "%s:%d" % (proxy.server, proxy.port)
            
        if _py26_or_greater():
            opener = urllib2.build_opener(urllib2.ProxyHandler(proxy_url), urllib2.HTTPHandler)
        else:
            opener = urllib2.build_opener(ConnectHTTPSHandler(proxy=proxy_url))
        urllib2.install_opener(opener)
        
    def build_http_request(self, uri, args, fmt):
        '''Construir la petición HTTP'''
        argStr = ''
        headers = {}
        response = ''
        argData = None
        encoded_args = ''
        method = "GET"
            
        for action in self.post_actions:
            if uri.endswith(action):
                method = "POST"
                break
        
        if args.has_key('id'):
            uri = "%s/%s" % (uri, args['id'])
            del args['id']
        
        uri = "%s.%s" % (uri, fmt)
        self.log.debug('Request to: %s' % uri)
        
        if len(args) > 0:
            s_args = []
            for k, v in args.items():
                if type(v) == 'str':
                    s_args.append((k, v.encode('utf-8')))
                else:
                    s_args.append((k, v))
            encoded_args = urlencode(s_args)
        
        if method == "GET":
            if encoded_args:
                argStr = "?%s" % (encoded_args)
        else:
            argData = encoded_args
        
        strReq = "%s%s" % (uri, argStr)
        req = TurpialHTTPRequest(argStr, headers, argData, encoded_args, 
            method, strReq, uri, args)
        return req
    
    def auth_http_request(self, httpreq, args):
        if self.oauth_support:
            signed_httpreq = self.__oauth_sign_http_request(httpreq, args)
        else:
            signed_httpreq = self.__basic_sign_http_request(httpreq, args)
        return signed_httpreq
        
    def fetch_http_resource(self, httpreq, fmt):
        req = urllib2.Request(httpreq.strReq, httpreq.argData, httpreq.headers)
        handle = urllib2.urlopen(req)
        response = handle.read()
        if fmt == 'json':
            return json.loads(response)
        else:
            return response
    
    def request(self, url, args={}, fmt=DEFAULT_FORMAT, base_url=None, secure=False):
        if not base_url:
            base_url = self.urls['api']
        if secure:
            base_url = base_url.replace('http://', 'https://')
        request_url = "%s%s" % (base_url, url)
        httpreq = self.build_http_request(request_url, args, fmt)
        authreq = self.auth_http_request(httpreq, self.auth_args)
        return self.fetch_http_resource(authreq, fmt)
    
class TurpialHTTPRequest:
    def __init__(self, argStr='', headers={}, argData=None, encoded_args='', 
        method="GET", strReq='', uri='', params={}):
        
        self.argStr = argStr
        self.headers = headers
        self.argData = argData
        self.encoded_args = encoded_args
        self.method = method
        self.strReq = strReq
        self.params = params
        self.uri = uri
        
    def __str__(self):
        
        return "method: %s\nencoded_args: %s\nargStr: %s\nargData: %s\n \
headers: %s\nstrReq: %s-" % (self.method, self.encoded_args, 
            self.argStr, self.argData, self.headers, self.strReq)
        
        pass
    
class ProxyHTTPConnection(httplib.HTTPConnection):

    _ports = {'http' : 80, 'https' : 443}


    def request(self, method, url, body=None, headers={}):
        #request is called before connect, so can interpret url and get
        #real host/port to be used to make CONNECT request to proxy
        proto, rest = urllib.splittype(url)
        if proto is None:
            raise ValueError, "unknown URL type: %s" % url
        #get host
        host, rest = urllib.splithost(rest)
        #try to get port
        host, port = urllib.splitport(host)
        #if port is not defined try to get from proto
        if port is None:
            try:
                port = self._ports[proto]
            except KeyError:
                raise ValueError, "unknown protocol for: %s" % url
        self._real_host = host
        self._real_port = port
        httplib.HTTPConnection.request(self, method, url, body, headers)
        

    def connect(self):
        httplib.HTTPConnection.connect(self)
        #send proxy CONNECT request
        self.send("CONNECT %s:%d HTTP/1.0\r\n\r\n" % (self._real_host, self._real_port))
        #expect a HTTP/1.0 200 Connection established
        response = self.response_class(self.sock, strict=self.strict, method=self._method)
        (version, code, message) = response._read_status()
        #probably here we can handle auth requests...
        if code != 200:
            #proxy returned and error, abort connection, and raise exception
            self.close()
            raise socket.error, "Proxy connection failed: %d %s" % (code, message.strip())
        #eat up header block from proxy....
        while True:
            #should not use directly fp probablu
            line = response.fp.readline()
            if line == '\r\n': break

class ProxyHTTPSConnection(ProxyHTTPConnection):
    
    default_port = 443

    def __init__(self, host, port = None, key_file = None, cert_file = None, strict = None):
        ProxyHTTPConnection.__init__(self, host, port)
        self.key_file = key_file
        self.cert_file = cert_file
    
    def connect(self):
        ProxyHTTPConnection.connect(self)
        #make the sock ssl-aware
        ssl = socket.ssl(self.sock, self.key_file, self.cert_file)
        self.sock = httplib.FakeSocket(self.sock, ssl)

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
       
