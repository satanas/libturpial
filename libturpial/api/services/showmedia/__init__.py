# -*- coding: utf-8 -*-

"""A list containing all show media services"""
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# 2012-08-01

from libturpial.api.services.showmedia.twitpic import TwitpicMediaContent
from libturpial.api.services.showmedia.yfrog import YfrogMediaContent
from libturpial.api.services.showmedia.instagram import InstagramMediaContent
from libturpial.api.services.showmedia.pictwitter import PicTwitterMediaContent
from libturpial.api.services.showmedia.youtube import YouTubeMediaContent
from libturpial.api.services.showmedia.foursquare import FoursquareMediaContent
from libturpial.api.services.showmedia.pinterest import PinterestMediaContent
from libturpial.api.services.showmedia.lockerz import LockerzMediaContent

SHOWMEDIA_SERVICES = {
    'twitpic': TwitpicMediaContent(),
    'yfrog': YfrogMediaContent(),
    'instagram': InstagramMediaContent(),
    'pic.twitter.com': PicTwitterMediaContent(),
    'youtube' : YouTubeMediaContent(),
    'foursquare' : FoursquareMediaContent()
    'pinterest': PinterestMediaContent(),
    'lockerz': LockerzMediaContent(),
}
