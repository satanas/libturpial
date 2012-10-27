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

Constants
---------

.. autoattribute:: libturpial.common.ProtocolType
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

Exceptions
----------

Module to handle custom exceptions for libturpial

.. module:: libturpial.common.exceptions

.. autoexception:: URLShortenError
.. autoexception:: NoURLException
.. autoexception:: UploadImageError

