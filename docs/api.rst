.. _api:

API
===

.. module:: libturpial

This part of the documentation covers all modules of libturpial.

Core
----

.. autoclass:: libturpial.api.core.Core
	:members:
	:undoc-members:
	:special-members:

Configuration
-------------

.. automodule:: libturpial.lib.config

Protocols
---------

Protocol.py
+++++++++++
.. autoclass:: libturpial.lib.interfaces.protocol.Protocol
	:members:
	:undoc-members:
	:private-members:
	:special-members:


Twitter
+++++++

.. autoclass:: libturpial.lib.protocols.twitter.twitter.Main
	:members:
	:undoc-members:
	:private-members:
	:special-members:

Identi.ca
+++++++++

.. autoclass:: libturpial.lib.protocols.identica.identica.Main
	:members:
	:undoc-members:
	:private-members:
	:special-members:

HTTP
----

.. automodule:: libturpial.lib.http

Constants
+++++++++

.. data:: DEFAULT_TIMEOUT

    Default time that TurpialHTTPBase waits until killing a request. Value: 20 (seconds)

.. data:: FORMAT_XML

    Constant to identify XML requests

.. data:: FORMAT_JSON

    Constant to identify JSON requests

TurpialHTTPBase
+++++++++++++++
.. autoclass:: libturpial.lib.http.TurpialHTTPBase
	:members:
	:undoc-members:
	:special-members:

TurpialHTTPOAuth
++++++++++++++++
.. autoclass:: libturpial.lib.http.TurpialHTTPOAuth
	:members:
	:undoc-members:
	:private-members:
	:special-members:

TurpialHTTPBasicAuth
++++++++++++++++++++
.. autoclass:: libturpial.lib.http.TurpialHTTPBasicAuth
	:members:
	:undoc-members:
	:private-members:
	:special-members:

TurpialHTTPRequest
++++++++++++++++++
.. autoclass:: libturpial.lib.http.TurpialHTTPRequest
	:members:

Constants
---------

.. autoattribute:: libturpial.common.ProtocolType

.. data:: STATUSPP

    Default value for the number of statuses fetched by request

.. data:: OS_LINUX

    Constant to identify Linux based operating systems

.. data:: OS_WINDOWS

    Constant to identify Windows operating systems

.. data:: OS_MAC

    Constant to identify Mac operating systems

.. data:: OS_JAVA

    Constant to identify Java based operating systems

.. data:: OS_UNKNOWN

    Constant to identify operating systems that does not belong to any of the previous categories

.. data:: HASHTAG_PATTERN

    Regex pattern to match microblogging hashtags (for example: #hashtags)

.. data:: MENTION_PATTERN

    Regex pattern to match microblogging mentions (for example: @user)

.. data:: CLIENT_PATTERN

    Regex pattern to match client names from an <a> tag

.. data:: URL_PATTERN

    Regex pattern to match URLs

.. data:: ERROR_CODES

    Dictionary with all error messages supported by libturpial

Exceptions
----------

Module to handle custom exceptions for libturpial

.. module:: libturpial.common.exceptions

.. autoexception:: URLShortenError
.. autoexception:: NoURLException
.. autoexception:: UploadImageError

