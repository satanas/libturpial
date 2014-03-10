# -*- coding: utf-8 -*-

"""Adapter for shorty-python libraries"""
#
# Author: Andrea Stagi (4ndreaSt4gi)
# 2010-07-28

from libturpial.lib.interfaces.service import GenericService


class ShortUrlAdapter(GenericService):
    def __init__(self, obj):
        GenericService.__init__(self)
        self._obj = obj

    def do_service(self, longurl):
        return self._obj.shrink(longurl)
