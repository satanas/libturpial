# -*- coding: utf-8 -*-

"""Módulo genérico para manejar las solicitudes HTTP de Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

import os
import socket
import urllib2
import urllib
import httplib
import logging

from base64 import b64encode
from urllib import urlencode

def _py26_or_greater():
    import sys
    return sys.hexversion > 0x20600f0

if _py26_or_greater():
    import json
else:
    import simplejson as json

class TurpialHTTP:
    DEFAULT_FORMAT = 'json'
    
    def __init__(self, post_actions):
        self.urls = {}
        self.auth_args = {}
        self.post_actions = post_actions
        self.log = logging.getLogger('TurpialHTTP')
        
        # timeout in seconds
        timeout = 20
        socket.setdefaulttimeout(timeout)
        
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
        
    def build_http_request(self, uri, args, format):
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
        
        uri = "%s.%s" % (uri, format)
        self.log.debug('URI: %s' % uri)
        
        if len(args) > 0:
            encoded_args = urlencode(args)
        
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
        username = args['username']
        password = args['password']
        if username:
            auth_info = b64encode("%s:%s" % (username, password))
            httpreq.headers["Authorization"] = "Basic " + auth_info
        return httpreq
        
    def fetch_http_resource(self, httpreq, format):
        req = urllib2.Request(httpreq.strReq, httpreq.argData, httpreq.headers)
        handle = urllib2.urlopen(req)
        if format == 'json':
            return json.loads(handle.read())
        else:
            return handle.read()
    
    def request(self, url, args={}, format=DEFAULT_FORMAT):
        request_url = "%s%s" % (self.urls['api'], url)
        self.log.debug('Making request to: %s' % request_url)
        httpreq = self.build_http_request(request_url, args, format)
        authreq = self.auth_http_request(httpreq, self.auth_args)
        return self.fetch_http_resource(authreq, format)
    
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
        '''
        return "method: %s\nencoded_args: %s\nargStr: %s\nargData: %s\n" + 
            "headers: %s\nstrReq: %s-" % (self.method, self.encoded_args, 
            self.argStr, self.argData, self.headers, self.strReq)
        '''
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
       
