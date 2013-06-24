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
	:members:
	:undoc-members:
	:special-members:

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
	:special-members:

.. autoattribute:: libturpial.api.protocols.twitter.params.POST_ACTIONS

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
	:special-members:

TurpialHTTPRequest
++++++++++++++++++
.. autoclass:: libturpial.lib.http.TurpialHTTPRequest
	:members:

Constants
---------

.. automodule:: libturpial.common
	:members:
	:undoc-members:

Exceptions
----------

Module to handle custom exceptions for libturpial

.. module:: libturpial.common.exceptions

.. autoexception:: URLShortenError
.. autoexception:: NoURLException
.. autoexception:: UploadImageError

