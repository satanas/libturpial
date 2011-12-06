# -*- coding: utf-8 -*-

# Tools for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 07, 2011

import os
import sys

OS_LINUX = 'linux'
OS_WINDOWS = 'windows'
OS_MAC = 'darwin'
OS_JAVA = 'java'
OS_UNKNOWN = 'unknown'

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
    elif sys.platform.startswith('win32'):
        return OS_WINDOWS
    elif sys.platform.startswith('darwin'):
        return OS_MAC
    elif sys.platform.startswith('java'):
        return OS_JAVA
    else:
        return OS_UNKNOWN
