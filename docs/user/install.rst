How to install libturpial
=========================

This part of the documentation covers the installation of libturpial.

Requirements
------------

libturpial needs this packages to work properly:

* Python >= 2.5
* simplejson >= 1.9.2
* OAuth

Distribute
----------

Installing libturpial is really simple with `pip <http://www.pip-installer.org/>`_::

    $ pip install libturpial

Cheeseshop Mirror
-----------------

If the Cheeseshop is down, you can also install libturpial from one of the
mirrors. `Crate.io <http://crate.io>`_ is one of them::

    $ pip install -i http://simple.crate.io/ libturpial


Get the code
------------

libturpial is under heavy development on GitHub, where the code is `always available <https://github.com/Turpial/libturpial>`_.

You can either clone the public repository::

    git clone git://github.com/Turpial/libturpial.git

Download the `tarball <https://github.com/Turpial/libturpial/tarball/master>`_::

    $ wget -c https://github.com/Turpial/libturpial/tarball/master

Once you have a copy of the source, you can embed it in your Python package,
or install it into your site-packages easily::

    $ python setup.py install
