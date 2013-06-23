# -*- coding: utf-8 -*-

class Proxy:
    """
    This class models the information of a proxy server used to establish an
    HTTP connection. *host* and *port* are required. For an authenticated
    proxy set *username* and *password* and if proxy uses HTTPS set *secure*
    to **True**, otherwise let it **False**

    Example to store the information of a HTTP proxy:

    >>> proxy = Proxy('127.0.0.1', '1234', 'my_user', 'secret_password')

    And for a HTTPS:

    >>> proxy = Proxy('127.0.0.1', '1234', 'my_user', 'secret_password', True)
    """
    def __init__(self, host, port, username='', password='', secure=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.secure = secure
