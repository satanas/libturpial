# -*- coding: utf-8 -*-

"""Generic module to handle HTTP requests in libturpial"""

import os
import ssl
import sys
import socket
import base64
import logging
import requests

try:
    import oauth.oauth as oauth
except:
    import oauth

DEFAULT_TIMEOUT = 20
FORMAT_XML = 'xml'
FORMAT_JSON = 'json'


class TurpialHTTPBase:
    """
    This class is the abstraction of the HTTP protocol for libturpial. It
    handles all the magic behind http requests: building, authenticating and
    fetching resources, in other words, it standarize the way you interact
    with end points and services.

    You shouldn't instantiate this class, instead you should use the proper
    implementation for OAuth
    (:class:`libturpial.api.interfaces.http.TurpialHTTPOAuth`)
    or Basic Auth
    (:class:`libturpial.api.interfaces.http.TurpialHTTPBasicAuth`)
    or even develop your own implementation if the authentication method is
    not supported.

    *base_url* is the part of the URL common for all your requests
    (http://api.twitter.com/1.1 for example). *proxies* is a dict where you
    define HTTP/HTTPS proxies.

    >>> proxies = {
    ...    "http": "http://10.10.1.10:3128",
    ...    "https": "https://10.10.1.10:1080",
    ... }

    If your proxy uses HTTP authentication then you can set user and password
    with something like this:

    >>> proxies = {
    ...    "http": "http://user:pass@10.10.1.10:3128",
    ... }

    *timeout* is the maximum time in seconds that TurpialHTTPBase will wait
    before cancelling the current request. If *timeout* is not specified
    then *DEFAULT_TIMEOUT* will be used.
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
                                                  '..', 'certs',
                                                  'cacert.pem'))

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
                    ssl_error_msg = "Host name '%s' doesn't match" \
                                    " certificate host '%s'"
                    raise ssl.SSLError(ssl_error_msg % (host, certhost))

        self.log.debug('Validated SSL cert for host: %s' % host)

    def __build_request(self, method, uri, args, _format, secure, id_in_url):
        if 'id' in args and id_in_url:
            uri = "%s/%s" % (uri, args['id'])
            del args['id']

        if _format is None:
            uri = "%s" % (uri)
        else:
            uri = "%s.%s" % (uri, _format)

        return TurpialHTTPRequest(method, uri, _format=_format, params=args,
                                  secure=secure)

    def __fetch_resource(self, httpreq):
        if httpreq.method == 'GET':
            req = requests.get(httpreq.uri, params=httpreq.params,
                               headers=httpreq.headers, verify=httpreq.secure,
                               proxies=self.proxies, timeout=self.timeout)
        elif httpreq.method == 'POST':
            req = requests.post(httpreq.uri, params=httpreq.params,
                                headers=httpreq.headers, verify=httpreq.secure,
                                proxies=self.proxies, timeout=self.timeout)
        if httpreq._format == FORMAT_JSON:
            return req.json()
        else:
            return req.text

    def sign_request(self, httpreq):
        """
        This is the method you need to overwrite if you subclass
        :class:`libturpial.api.interfaces.http.TurpialHTTPBase`.

        *httpreq* is the current request
        (a :class:`libturpial.api.interfaces.http.TurpialHTTPRequest`
        object), you need to apply all the authentication/authorization methods
        to that object and make it valid; then exit. There is no need to return
        any value because all changes are done directly over the object.

        If this method is not overwritten it will return a
        **NotImplementedError** exception.
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # Main Methods
    # ------------------------------------------------------------

    def set_timeout(self, timeout):
        """
        Configure the maximum time (in seconds) to wait before killing the
        current request.
        """
        self.timeout = timeout

    def set_proxy(self, host, port, username='', password='', https=False):
        """
        Set an HTTP/HTTPS proxy for all requests. You must pass the *host*
        and *port*. If your proxy uses HTTP authentication you can pass the
        *username* and *password* too. If *https* is True your proxy will
        use HTTPS, otherwise HTTP.
        """
        proxy_auth = ''
        if username and password:
            proxy_auth = "%s:%s@" % (username, password)

        protocol = 'https' if https else 'http'
        self.proxies[protocol] = "%s://%s%s:%s" % (protocol, proxy_auth,
                                                   host, port)

    def get(self, uri, args=None, _format=FORMAT_JSON, base_url=None,
            secure=False, id_in_url=True):
        """
        Performs a GET request against the *uri* resource with *args*. You
        can specify the *_format* ('json' or 'xml') and can specify a different
        *base_url*. If *secure* is True the request will be perform as HTTPS,
        otherwise it will be performed as HTTP.

        This method is an alias for **request** function using 'GET' as method.
        """
        return self.request('GET', uri, args, _format, base_url, secure,
                            id_in_url)

    def post(self, uri, args=None, _format=FORMAT_JSON, base_url=None,
             secure=False, id_in_url=True):
        """
        Performs a POST request against the *uri* resource with *args*. You
        can specify the *_format* ('json' or 'xml') and can specify a different
        *base_url*. If *secure* is True the request will be perform as HTTPS,
        otherwise it will be performed as HTTP.

        This method is an alias for **request** function using 'POST' as method
        """
        return self.request('POST', uri, args, _format, base_url, secure,
                            id_in_url)

    def request(self, method, uri, args=None, _format=FORMAT_JSON,
                alt_base_url=None, secure=False, id_in_url=True):
        """
        Performs a GET or POST request against the *uri* resource with
        *args*. You can specify the *_format* ('json' or 'xml') and can specify
        a different *base_url*. If *secure* is True the request will be perform
        as HTTPS, otherwise it will be performed as HTTP
        """

        args = args or {}
        base_url = alt_base_url or self.base_url

        if secure:
            base_url = base_url.replace('http://', 'https://')
            self.__validate_ssl_cert(base_url)

        request_url = "%s%s" % (base_url, uri)

        httpreq = self.__build_request(method, request_url, args, _format,
                                       secure, id_in_url)
        self.sign_request(httpreq)
        return self.__fetch_resource(httpreq)


class TurpialHTTPOAuth(TurpialHTTPBase):
    """
    Implementation of TurpialHTTPBase for OAuth. *base_url* is the part of
    the URL common for all your requests
    (http://api.twitter.com/1.1 for example). *oauth_options* is a dict with
    all the OAuth configuration parameters. It must looks like:

    >>> oauth_options = {
    ...    'consumer_key': 'APP_CONSUMER_KEY',
    ...    'consumer_secret': 'APP_CONSUMER_SECRET',
    ...    'request_token_url': 'http://request_url',
    ...    'authorize_token_url': 'http://authorize_url',
    ...    'access_token_url': 'http://access_url',
    ... }

    *consumer_key* and *consumer_secret* are the credentials for your
    application (they must be provided by the OAuth service).
    *request_token_url*, *authorize_token_url* and *access_token_url* are
    the URLs designed by the OAuth service to fetch and authorize an OAuth
    token.

    *user_key*, *user_secret* and *verifier* (a.k.a. PIN) are the token
    credentials granted to the user after the OAuth dance. They are optional
    and needed only if the user was already authenticated, otherwise you need
    to fetch a new token.

    *proxies* and *timeout* work in the same way that in
    :class:`libturpial.api.interfaces.http.TurpialHTTPBase`.

    * To request an OAuth token create a new TurpialHTTPOAuth object and
      request a token to your service:

    >>> base_url = 'http://api.twitter.com/1.1'
    >>> http = TurpialHTTPOAuth(base_url, oauth_options)
    >>> url_to_auth = http.request_token()

    Ask the user go to the *url_to_auth* URL and authorize your app. Then get
    the PIN the service will deliver to your user and authorize the token:

    >>> pin = '123456'
    >>> token = http.authorize_token(pin)

    Use this token to store the key, secret and pin in a safe place to use it
    from now on. Then inform to TurpialHTTPOAuth that you have access granted:

    >>> http.set_token_info(token.key, token.secret, token.verifier)

    * To use an existing token to fetch a resource create a new
      TurpialHTTPOAuth object and pass the user_key, user_secret and
      pin (verifier):

    >>> user_key = 'example'
    >>> user_secret = 'example'
    >>> verifier = 'example'
    >>> http = TurpialHTTPOAuth(base_url, oauth_options, user_key, user_secret,
    ...                         verifier)

    * To perform a request use the get or post method:

    >>> http.get('/my_first/end_point', args={'arg1': '1'}, _format='json')
    >>> http.post('/my_second/end_point', args={'arg1': '2'}, _format='json')

    """
    def __init__(self, base_url, oauth_options, user_key=None,
                 user_secret=None, verifier=None, proxies=None,
                 timeout=None):
        TurpialHTTPBase.__init__(self, base_url, proxies, timeout)

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

    def sign_request(self, httpreq):
        """
        Signs the *httpreq* for OAuth using the previously defined user token
        """
        request = \
            oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                                                       token=self.token,
                                                       http_method=httpreq.method,  # noqa
                                                       http_url=httpreq.uri,
                                                       parameters=httpreq.params)  # noqa

        request.sign_request(self.sign_method_hmac_sha1, self.consumer,
                             self.token)
        httpreq.headers.update(request.to_header())

    def set_token_info(self, user_key, user_secret, verifier):
        """
        Creates a new token using the existing *user_key*, *user_secret* and
        *verifier*. Use this method
        """
        self.token = oauth.OAuthToken(user_key, user_secret)
        self.token.set_verifier(verifier)

    def request_token(self):
        """
        Ask to the service for a fresh new token. Returns an URL that the
        user must access in order to authorize the client.
        """
        oauth_request = \
            oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                                                       http_url=self.request_token_url)  # noqa

        oauth_request.sign_request(self.sign_method_hmac_sha1, self.consumer,
                                   None)

        req = requests.get(self.request_token_url,
                           headers=oauth_request.to_header())
        self.token = oauth.OAuthToken.from_string(req.text)

        oauth_request = \
            oauth.OAuthRequest.from_token_and_callback(token=self.token,
                                                       http_url=self.authorize_token_url)  # noqa

        return oauth_request.to_url()

    def authorize_token(self, pin):
        """
        Uses the *pin* returned by the service to authorize the current token.
        Returns an :class:`oauth.OAuthToken` object.
        """
        oauth_request = \
            oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                                                       token=self.token,
                                                       verifier=pin,
                                                       http_url=self.access_token_url)  # noqa

        oauth_request.sign_request(self.sign_method_hmac_sha1, self.consumer,
                                   self.token)

        req = requests.get(self.access_token_url,
                           headers=oauth_request.to_header())
        self.token = oauth.OAuthToken.from_string(req.text)

        return self.token

    def request_xauth_token(self, username, password):
        """
        Request a limited token without using the whole OAuth flow, it just
        uses the username and password through xAuth
        """
        request = oauth.OAuthRequest.from_consumer_and_token(
            oauth_consumer=self.consumer,
            http_method='POST', http_url=self.access_token_url,
            parameters={
                'x_auth_mode': 'client_auth',
                'x_auth_username': username,
                'x_auth_password': password
            }
        )
        request.sign_request(self.sign_method_hmac_sha1, self.consumer, None)

        req = requests.post(self.access_token_url, data=request.to_postdata())
        self.token = oauth.OAuthToken.from_string(req.text)

        return self.token


class TurpialHTTPBasicAuth(TurpialHTTPBase):
    """
    Implementation of TurpialHTTPBase for the HTTP Basic Authentication.
    *base_url* is the part of the URL common for all your requests
    (http://identi.ca/api for example). *username* and *password* are the
    username credentials. *proxies* and *timeout* work in the same way
    that in :class:`libturpial.api.interfaces.http.TurpialHTTPBase`.

    *proxies* and *timeout* work in the same way that in
    :class:`libturpial.api.interfaces.http.TurpialHTTPBase`.

    * To fetch a resource using Basic Authentication just create a new
      TurpialHTTPBasicAuth object and pass the user credentials as parameters:

    >>> base_url = 'http://identi.ca/api'
    >>> username = 'example'
    >>> password = 'example'
    >>> http = TurpialHTTPBasicAuth(base_url, username, password)

    Then perform the request desired using get or post methods:

    >>> http.get('/my_first/end_point', args={'arg1': '1'}, _format='json')
    >>> http.post('/my_second/end_point', args={'arg1': '2'}, _format='json')

    """
    def __init__(self, base_url, proxies=None, timeout=None):
        TurpialHTTPBase.__init__(self, base_url, proxies, timeout)

    def set_user_info(self, username, password):
        """
        Set the *username* and *password* for the basic authentication
        """
        auth_info = base64.b64encode("%s:%s" % (username, password))
        self.basic_auth_info = ''.join(["Basic ", auth_info])

    def sign_request(self, httpreq):
        """
        The *httpreq* is signed using the Authorization header as
        documented in the `Basic Access Authentication Wiki
        <http://en.wikipedia.org/wiki/Basic_access_authentication>`_
        """
        httpreq.headers["Authorization"] = self.basic_auth_info


class TurpialHTTPRequest:
    """
    Encapsulate an URL request into a python object
    """
    def __init__(self, method, uri, headers=None, params=None,
                 _format=FORMAT_JSON, secure=False):

        self.uri = uri
        self.method = method
        self._format = _format
        self.secure = secure
        self.params = params or {}
        self.headers = headers or {}
