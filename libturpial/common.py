# -*- coding: utf-8 -*-

""" Common variables for Turpial API """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 13, 2011

import os
import sys

VERSION = '0.7.0-a2'
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
