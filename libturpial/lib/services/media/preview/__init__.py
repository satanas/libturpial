# -*- coding: utf-8 -*-

"""A list containing all show media services"""
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# 2012-08-01

from libturpial.lib.services.media.preview.imgur import ImgurMediaContent
from libturpial.lib.services.media.preview.lockerz import LockerzMediaContent
from libturpial.lib.services.media.preview.twitpic import TwitpicMediaContent
from libturpial.lib.services.media.preview.yfrog import YfrogMediaContent
from libturpial.lib.services.media.preview.instagram import InstagramMediaContent
from libturpial.lib.services.media.preview.pictwitter import PicTwitterMediaContent
from libturpial.lib.services.media.preview.viame import ViameMediaContent
from libturpial.lib.services.media.preview.flickr import FlickrMediaContent
from libturpial.lib.services.media.preview.youtube import YouTubeMediaContent
from libturpial.lib.services.media.preview.foursquare import FoursquareMediaContent

PREVIEW_MEDIA_SERVICES = {
    'imgur': ImgurMediaContent(),
    'lockerz': LockerzMediaContent(),
    'twitpic': TwitpicMediaContent(),
    'yfrog': YfrogMediaContent(),
    'instagram': InstagramMediaContent(),
    'pic.twitter.com': PicTwitterMediaContent(),
    'via.me': ViameMediaContent(),
    'flic.kr': FlickrMediaContent(),
#    'youtube' : YouTubeMediaContent(),
    'foursquare': FoursquareMediaContent()
}
