libturpial
==========

**Summary:** A powerful microblogging library written in Python

*libturpial* is a library that handles multiple microblogging protocols. It 
implements a lot of features and aims to support all the features for each 
protocol. At the moment it supports Twitter and Identi.ca and is the backend 
used for *Turpial*.

Currently  *libturpial* is in heavy development, so probably you will find bugs or 
undesired behavior. In this cases please report issues at:

http://dev.turpial.org.ve/projects/libturpial/issues

We will be very graceful for your contributions.


License
-------

*libturpial* source code, images and sounds have been released under the *GPL v3* 
License. Please check the ``COPYING`` file for more details or visit 
http://www.gnu.org/licenses/gpl-3.0.html


Requirements
------------

libturpial needs this packages to work properly:

 * ``python >= 2.5``
 * ``simplejson >= 1.9.2`` (python-simplejson)
 * ``oauth``  (python-oauth)
 * ``setuptools`` (python2-distribute)
 * ``pkg-resources``


Installation
------------

libturpial should be available on most popular Linux distributions, so you are 
able to install it using your favorite package manager (aptitude, apt-get, 
pacman, yum). Please visit http://turpial.org.ve/downloads for more information.

To install libturpial from sources you should go to source folder and 
run (as superuser)::

    # python setup.py install

or using ``sudo``::

    $ sudo python setup.py install


Documentation
-------------

To generate the documentation and learn how to use libturpial install sphinx
and run::

    $ sphinx-build -a -b html docs/ my_output_folder/

Then check index.html in **my_output_folder**


Further Information
-------------------

For more information visit our FAQ page http://turpial.org.ve/faqs/


Contact
-------

You can follow libturpial news from our official Twitter account:

 * @TurpialVe

Join to the official development mailing list:

http://groups.google.com/group/turpial-dev

Or mail us to say what an awesome/crappy app libturpial is. Our contact info is
in:

http://turpial.org.ve/team


Donate
------

You love libturpial and want to show us how gracefull you are? Buy us a coffee :)

PayPal donations at:

https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XUNXXJURA7FLW

Flattr:

http://flattr.com/thing/452623/Turpial

