# -*- coding: utf-8 -*-

"""Utils for show media content services"""
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# 2010-08-02

from libturpial.api.services.showmedia import SHOWMEDIA_SERVICES

def get_service_from_url(url):
    for service in SHOWMEDIA_SERVICES:
        if SHOWMEDIA_SERVICES[service].can_manage_url(url):
            return SHOWMEDIA_SERVICES[service]
    return None

def is_service_supported(url):
    if get_service_from_url(url) != None:
        return True
    return False
