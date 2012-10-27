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
	:private-members:
	:special-members:

Exceptions
----------

Module to handle custom exceptions for libturpial

.. module:: libturpial.common.exceptions

.. autoexception:: URLShortenError
.. autoexception:: NoURLException
.. autoexception:: UploadImageError

Configuration
-------------

.. automodule:: libturpial.config

Protocols
---------

Twitter
+++++++

.. autoclass:: libturpial.api.protocols.twitter.twitter.Main
	:members:
	:undoc-members:
	:private-members:
	:special-members:

Identi.ca
+++++++++

.. autoclass:: libturpial.api.protocols.identica.identica.Main
	:members:
	:undoc-members:
	:private-members:
	:special-members: