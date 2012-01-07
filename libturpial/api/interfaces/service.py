# -*- coding: utf-8 -*-

"""Interface for services"""
#
# Author: Wil Alvarez (aka Satanas)
# 2010-04-18

import urllib2
import logging

try:
    import json
except ImportError:
    import simplejson as json

class GenericService:
    def __init__(self):
        self.log = logging.getLogger('Service')

    def _get_request(self, url, data=None):
        ''' Process a GET request and returns a text plain response '''
        self.log.debug('GET Request: %s' % url)
        return urllib2.urlopen(url, data).read()
        
    def _json_request(self, url):
        ''' Process a GET request and returns a json hash '''
        self.log.debug('JSON Request: %s' % url)
        return json.loads(urllib2.urlopen(url).read())
        
    def _quote_url(self, url):
        longurl = urllib2.quote(url)
        longurl = longurl.replace('/', '%2F')
        return longurl
            
    def _parse_xml(self, key, xml):
        """ Simple XML parser """
        key = key.lower()
        for tag in xml.split("<"):
            tokens = tag.split()
            if tokens and tokens[0].lower().startswith(key):
                return tag.split(">")[1].strip()
        
    def do_service(self, arg):
        raise NotImplementedError
        
class ServiceResponse:
    def __init__(self, response=None, err=False, err_msg=None):
        self.response = response
        self.err = err
        self.err_msg = err_msg

class URLShortenError(Exception):
    def __init__(self, message):
        self.message = message

class UploadImageError(Exception):
    def __init__(self, message):
        self.message = message
