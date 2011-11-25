# -*- coding: utf-8 -*-

"""A list containing all short url services"""
#
# Author: Andrea Stagi (4ndreaSt4gi)
# 2010-07-28

from shortypython.shorty import services
from shorturladapter import ShortUrlAdapter

URL_SERVICES = {}

for k in services:
    URL_SERVICES[k] = ShortUrlAdapter(services[k])
