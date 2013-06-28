.. _config:

Configuration
=============

This module contains all the classes involved in Turpial configuration.
All files are stored on *~/.config/turpial/* and cache is stored on 
*~/.cache/turpial/*. Absolutes directories will vary depending on the
operating system.

In configuration folder you will find:

* accounts: A directory where live sub-directories with the configuration of
  every single account.
* config: The global configuration file. Here is stored all the settings 
  related to the application behavior (even for the graphic interface)
* filtered: A plain text file where libturpial stores all filters applied to
  timelines.
* friends: A plain text file that contains the list of all the friends of 
  all the accounts registered

.. automodule:: libturpial.config
    :members:


