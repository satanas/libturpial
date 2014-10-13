# -*- coding: utf-8 -*-

# Tools for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 07, 2011

import os
import sys
import time

from libturpial.common import *


def clean_bytecodes(root_path, logger=None):
    """Clean all .pyc y .pyo. This is intented to use by all UI interfaces"""
    if logger:
        logger.debug("Cleaning da house...")

    path = os.path.join(os.path.dirname(root_path))
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
    elif sys.platform.startswith('freebsd'):
        return OS_FREEBSD
    elif sys.platform.startswith('dragonfly'):
        return OS_DFLY
    elif sys.platform.startswith('win32'):
        return OS_WINDOWS
    elif sys.platform.startswith('darwin'):
        return OS_MAC
    elif sys.platform.startswith('java'):
        return OS_JAVA
    else:
        return OS_UNKNOWN


def get_urls(text):
    """Returns all URL patterns encountered in text"""
    urls = []
    forbidden = [')', '.']
    for item in URL_PATTERN.findall(text):
        url = item[0]
        # Removes the last parenthesis
        if url[-1] in forbidden:
            url = url[:-1]
        urls.append(url)
    return urls

def timestamp_to_localtime(timestamp):
    """
    Take the long integer *timestamp* that represents an Unix timestamp and adjust it to
    local time, considering time zone and stuff.
    """
    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
    return timestamp - offset
