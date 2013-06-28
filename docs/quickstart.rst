.. _quickstart:

Quickstart
==========

Are you eager to start coding? Take a look to this section, it will get you a 
quick introduction on how to use libturpial.

Before start, you must check that libturpial is installed and up-to-date.
Check our `Wiki page for installing libturpial <http://wiki.turpial.org.ve/dev:installation>`_

Create an account
-----------------

First thing you need to use libturpial is an account. To create an account 
import the account module:

>>> from libturpial.api.models.account import Account

Let's create a new Twitter account:

>>> account = Account.new('twitter')

This account it's empty, hence pretty useless, except for one thing: 
authentication. Before you can make real use of an account it must be 
authenticated. To achieve that, let's ask for OAuth access:

>>> url = account.request_oauth_access()

This will return an OAuth valid URL that you must visit. In this case,
it will redirect you to Twitter, so you can authorize Turpial as a
third party app. Then copy the PIN (for example: '1234567') returned by 
Twitter and authorize the account:

>>> account.authorize_oauth_access('1234567')

Now you have a valid libturpial account to play with. Remember that this
account is not stored in disk yet. To save credentials you need to read
how to register the account.

Register the account
--------------------

Let's assume that you have the same account of the previous section (valid and 
authenticated). To register the account (and with this, save the credentials on
disk) you need a new instance of Core. First, let's import the Core module:

>>> from libturpial.api.core import Core

And now, let's instantiate Core:

>>> core = Core()

At this moment, Core will try to load any previous registered account to make it 
available. This shouldn't take more than a few seconds (that time could vary 
depending on your internet connection). When done, we can
register our fresh-new account created in the previous section. To do so:

>>> my_account_id = core.register_account(account)

That will return the account id if everything went fine.

It's important that you see the Core as a director, it can handle a lot of 
things at once but we need to specify exactly where to perform what we want to 
do. That's the reason why almost all methods on core receive as first argument
the account_id, it's like if you must to tell:

::

    Core, on this account do that.

It's not hard once you get used, it's like: `"sudo make me a sandwich"`__ ;)

Fetch the timeline
------------------

Now that we have a registered account we would be able to tinker a little bit with
Twitter. Let's fetch the account timeline:

>>> timeline = core.get_column_statuses(my_account_id, 'timeline', count=5)

You can print each retrieved status with:

>>> for status in timeline:
...     print status
...
<libturpial.api.models.status.Status instance at 0x1031583f8>
<libturpial.api.models.status.Status instance at 0x103159050>
<libturpial.api.models.status.Status instance at 0x1031590e0>
<libturpial.api.models.status.Status instance at 0x1031731b8>
<libturpial.api.models.status.Status instance at 0x103173320>

But wait, those are just :class:`libturpial.api.models.status.Status` object.
Let's print something more useful:

>>> for status in timeline:
...     print "@%s: %s" % (status.username, status.text)
...
@lombokdesign: La calidad de un link #infografia #infographic #internet #marketing http://t.co/8UF3m0QiAK
@TheHackersNews: Edward #Snowden's Father 》My Son Is Not A Traitor http://t.co/y6j8uB6832 #nsa
@Lavinotintocom: #FutVe Buda Torrealba espera alejarse de las lesiones http://t.co/XX53yCY2zv
@Lavinotintocom: #Eliminatorias César Farías: “Seguimos teniendo fe” #Vinotinto http://t.co/QfiMsxpAg9
@razonartificial: SDL 2.0: Release Candidate lista  http://t.co/B6jVOLly3Y vía @genbetadev

Interesting, isn't? We can play with all the available attributes of the status 
object. Check the status_ reference for more information.

With the *get_column_statuses* we can fetch statuses from any available column, 
you just need to change 'timeline' for the desired column.

Fetch any other column
----------------------

We already know how to fetch the timeline, but what about if we want to fetch 
any other column? Or even an user list? Well, let's check first which are the 
available options:

>>> all_columns = core.all_columns()

This will return a dict with all the available columns per account, so let's 
print the slug of each one:

>>> for key, columns in all_columns.iteritems():
...     print "For %s account:" % key
...     for column in columns:
...         print "  %s" % column.slug
...
For foo-twitter account:
  timeline
  replies
  directs
  sent
  favorites

Now we can fetch some other statuses, for example our favorites:

>>> favorites = core.get_column_statuses(my_account_id, 'favorites')

Or maybe our directs:

>>> directs = core.get_column_statuses(my_account_id, 'directs')

Working with statuses
---------------------

Update a status is as simple as:

>>> core.update_status(my_account_id, 'Test from libturpial')

If you want to reply a status made by a friend (identified with the id '123456789') 
then you will need to do something like this:

>>> core.update_status(my_account_id, '@foouser Hey! I am answering your tweet', '123456789')

You can even broadcast a status throught several accounts passing a
list with all the account and the text you want to update:

>>> core.broadcast_status([my_account_id1, my_account_id2], 'This is a broadcast test')

Let's say that you loved a tweet recently posted by a friend and identified by 
the id '123456789', it's easy mark it as favorite:

>>> core.mark_status_as_favorite(my_account_id, '123456789')

Besides, you want to share that lovely tweet with all your followers? No 
problem:

>>> core.repeat_status(my_account_id, '123456789')

You realize about that nasty tweet on your favs? Get ride off it:

>>> core.unmark_as_favorite(my_account_id, '123456789')

Posted a tweet with a typo again? Let's delete that mistake:

>>> core.destroy_status(my_account_id, '123456789')

And there are more methods that you can use to handle your statuses. Just take
a look to the core_ documention.

Managing your friendship
------------------------

Another interesing features about libturpial is that it lets you handle your 
friends.

Let's assume that you love the tweets that @a_lovely_account do every day. Well
you can follow that account with:

>>> core.follow(my_account_id, 'a_lovely_account')

Or probably you're tired of those boring tweets of @boring_friend, just 
unfollow (it's therapeutic):

>>> core.unfollow(my_account_id, 'boring_friend')

But look, you and I know that always there are bots that bother you every 
single minute, let's block them:

>>> core.block(my_account_id, 'annoying_bot')

And report it as spam:

>>> core.report_as_spam(my_account_id, 'annoying_bot')

That way Twitter can do something about it.

Now, there is this friend that you really love but he takes seriously the
unfollow thing and you are just tired of the no-sense tweets he does. No
problem, `mute` is for you:

>>> core.mute('my_psycho_friend')

With mute, libturpial simply hides all the tweets related to this guy 
without unfollow him. He will never notice that you are not reading his
post. Neat, isn't? ;)

But wait, this action is reversible. You can give him voice again:

>>> core.unmute('my_psycho_friend')

A final tip, do you want to know if @your_fav_account follows you? Use 
this:

>>> core.verify_friendship(my_account_id, 'your_fav_account')

This return `True` if they actually follows you or `False` otherwise.

Services
--------

libturpial include support for short URLs, upload pictures and preview pictures.
For the first two you can chose which to use from a wide of options. To check
which services are available for shorten URL:

>>> core.available_short_url_services()
['snipr.com', 'short.to', 'twurl.nl', 'buk.me', 'ub0.cc', 'fwd4.me', 'short.ie', 'burnurl.com', 'git.io', 'hurl.ws', 'digg.com', 'tr.im', 'budurl.com', 'urlborg.com', 'bit.ly', 'snipurl.com', 'a.gd', 'fon.gs', 'xr.com', 'sandbox.com', 'kl.am', 'snurl.com', 'to.ly', 'hex.io', 'migre.me', 'chilp.it', 'cli.gs', 'is.gd', 'sn.im', 'ur1.ca', 'tweetburner.com', 'x.bb', 'tinyurl.com', 'goo.gl']

You can verify which one is currently selected:

>>> core.get_shorten_url_service()
'migre.me'

And even select a different one:

>>> core.set_shorten_url_service('is.gd')

To short a long URL, do something like this:

>>> core.short_single_url('http://turpial.org.ve/news/')
'http://is.gd/Qq7Cdo'

But there is more, you can short all the URLs detected in a bunch of text:

>>> message = "This is the URL of the libturpial documentation source https://github.com/satanas/libturpial/tree/development/docs"
>>> new_message = core.short_url_in_message(message)
>>> print new_message
This is the URL of the libturpial documentation source http://is.gd/BJn0WO

To upload images the process is kind of similar. You check the available
services:

>>> core.available_upload_media_services()
['mobypicture', 'yfrog', 'twitpic', 'twitgoo', 'img.ly']

Verify the current one selected:

>>> core.get_upload_media_service()
'yfrog'

And select a different one:

>>> core.set_upload_media_service('twitpic')

Now, to upload a picture you only need the absolute path to the file and maybe
a message to post within the picture (only if the service allows pictures with
messages):

>>> core.upload_media(my_account_id, '/path/to/my/image.png', 'This is my pretty picture')
'http://twitpic.com/cytmf2'

Almost all services support JPEG, PNG and GIF format.

libturpial also handle the previsulization process of tweeted images for you.
Imagine that your best friend posted a picture and you want to see it, just
fetch the image with:

>>> preview = core.preview_media('http://twitpic.com/cytmf2')

libturpial will fetch the image and will store it on a temporary file, 
returning a :class:`libturpial.api.models.media.Media` object. You can get the
path of the temporary image with:

>>> preview.path
'/var/folders/1b/sq85x9v95nl44d2ccdb0_kmc0000gp/T/twitpic.com_cytmf2.jpg'

And even check if it's really an image (libturpial will support image, video
and maps on the near future):

>>> preview.is_image()
True

Further information
-------------------

Previous sections were a brief introduction to the whole power of libturpial.
For more information please check the `full documentation`_


.. _`"sudo make me a sandwich"`: http://imgs.xkcd.com/comics/sandwich.png
.. _status: api.html#status
.. _core: api.html#core
.. __`full documentation`: index
