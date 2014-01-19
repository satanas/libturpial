# -*- coding: utf-8 -*-

class Proxy:
    """
    This class models the information of a proxy server used to establish an
    HTTP connection. *host* and *port* are required. For an authenticated
    proxy set *username* and *password* with according credentilas and if 
    proxy uses HTTPS set *secure* to **True**, otherwise let it empty or 
    **False**

    For example, to store the information of a non-authenticated HTTPS proxy:

    >>> proxy = Proxy('127.0.0.1', '1234', secure=True)

    And for an authenticated HTTP proxy:

    >>> proxy = Proxy('127.0.0.1', '1234', 'my_user', 'secret_password')

    :ivar host: Proxy host address
    :ivar port: Proxy port
    :ivar username: (Optional) Username for authentication
    :ivar password: (Optional) Password for authentication
    :ivar secure: Indicate whether proxy uses HTTP or HTTPS (Default `False`)
    """
    def __init__(self, host, port, username=None, password=None, secure=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.secure = secure

    def to_url_config(self):
        if self.host == '' and self.port == '':
            return {}

        key = 'https' if self.secure else 'http'

        value = ''
        if self.host.find('http') < 0:
            value = "%s://" % key

        if self.username and self.password:
            value += "%s:%s@" % (self.username, self.password)

        value += self.host

        if self.port != '':
            value += ":%s" % self.port

        return {key: value}
