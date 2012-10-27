.. libturpial documentation master file, created by
   sphinx-quickstart on Thu Oct 25 22:17:19 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

libturpial: A microblogging client writen in Python, functional and beautiful
=============================================================================

*libturpial* is a library that handles multiple microblogging protocols. It implements a lot of features and aims to support all the features for each protocol. At the moment it supports Twitter_ and `Identi.ca`_ and is the backend used for Turpial_.

libturpial is currently under heavy development, so probably you will find bugs or undesired behavior. In this cases please report issues at:

https://github.com/Turpial/libturpial/issues

We will be very graceful for your contributions.

Feature support
---------------

- Twitter API
- Identi.ca API
- HTTP and OAuth authentication
- Proxy
- Services for shorten URL and upload images
- Multiple accounts
- Image preview
- Filtering expressions

User Guide
----------

This part of the documentation begins with some background information about libturpial, then focuses on step-by-step instructions for getting the most out of this library.

.. toctree::
   :maxdepth: 2

   user/intro
   user/install
   user/quickstart

API Documentation
-----------------

This part of the documentation shows you details about specific functions, methods and classes in libturpial.

.. toctree::
   :maxdepth: 2

   api

More information
----------------

For more information about the development process, please go to:

http://wiki.turpial.org.ve/dev:welcome


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Turpial: http://turpial.org.ve
.. _Twitter: http://twitter.com
.. _Identi.ca: http://identi.ca
