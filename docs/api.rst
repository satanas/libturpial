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

.. automodule:: libturpial.config
	:members:
	:undoc-members:
	:special-members:

Protocols
---------

List of protocols supported by libturpial

Twitter
+++++++

.. autoclass:: libturpial.api.protocols.twitter.twitter.Main
	:members:
	:undoc-members:
	:special-members:

.. autoattribute:: libturpial.api.protocols.twitter.params.POST_ACTIONS

Identi.ca
+++++++++

.. autoclass:: libturpial.api.protocols.identica.identica.Main
	:members:
	:undoc-members:
	:special-members:

.. autoattribute:: libturpial.api.protocols.identica.params.POST_ACTIONS


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

