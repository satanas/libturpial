# -*- coding: utf-8 -*-

"""A list containing all show media services"""
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# 2012-08-01

from twitpic import TwitpicMediaContent
from yfrog import YfrogMediaContent

SHOWMEDIA_SERVICES = {
    'twitpic' : TwitpicMediaContent(),
    'yfrog' : YfrogMediaContent()
}