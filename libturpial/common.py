# -*- coding: utf-8 -*-

""" Common variables for Turpial API """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 13, 2011

import os
import sys

VERSION = '0.8.0-a1'
STATUSPP = 20
OS_LINUX = 'linux'
OS_WINDOWS = 'windows'
OS_MAC = 'darwin'
OS_JAVA = 'java'
OS_UNKNOWN = 'unknown'

class ProtocolType:
    TWITTER = 'twitter'
    IDENTICA = 'identica'

class UpdateType:
    DM = 'dm'
    STD = 'std'
    PROFILE = 'profile'

class ColumnType:
    TIMELINE = 'timeline'
    REPLIES = 'replies'
    DIRECTS = 'directs'
    SENT = 'sent'
    FAVORITES = 'favorites'

ERROR_CODES = {
    100: "",
    304: "There was no new data to return",
    401: "Invalid or missing credentials",
    404: "Your argument is invalid",
    406: "What are you trying to search?",
    420: "Wait! Your search is being too intense",
    
    500: "Oops! The server is broken",
    502: "Oh oh... The server is down",
    503: "The server is overloaded",
    
    801: "There are some network issues",
    802: "Your status was sent. Don't try again",
    803: "User is already a friend",
    804: "You've already requested to follow that user",
    805: "Invalid account",
    806: "That column doesn't exist",
    807: "Server is not responding",
    808: "Accounr already logged in",
    
    900: "Feature not implemented yet",
    999: "Unknown error",
}
    
def clean_bytecodes(root_path, logger=None):
    """Clean all .pyc y .pyo. This is intented to use by all UI interfaces"""
    if logger:
        logger.debug("Cleaning da house...")
    
    path = os.path.join(os.path.dirname(root_path))
    i = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            path = os.path.join(root, f)
            if path.endswith('.pyc') or path.endswith('.pyo'): 
                if logger:
                    logger.debug("Deleting %s" % path)
                os.remove(path)
    if logger:
        logger.debug("Everything is clean now")
        
def detect_os():
    """ Returns a string according to the OS host """
    if sys.platform.startswith('linux'):
        return OS_LINUX
    elif sys.platform.startswith('win32'):
        return OS_WINDOWS
    elif sys.platform.startswith('darwin'):
        return OS_MAC
    elif sys.platform.startswith('java'):
        return OS_JAVA
    else:
        return OS_UNKNOWN
