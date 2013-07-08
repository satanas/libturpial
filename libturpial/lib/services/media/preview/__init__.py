# -*- coding: utf-8 -*-

"""A list containing all show media services"""

from .imgur import ImgurMediaContent
from .lockerz import LockerzMediaContent
from .twitpic import TwitpicMediaContent
from .yfrog import YfrogMediaContent
from .pictwitter import PicTwitterMediaContent
from .viame import ViameMediaContent
from .flickr import FlickrMediaContent

PREVIEW_MEDIA_SERVICES = {
    'imgur': ImgurMediaContent(),
    'lockerz': LockerzMediaContent(),
    'twitpic': TwitpicMediaContent(),
    'yfrog': YfrogMediaContent(),
    'pic.twitter.com': PicTwitterMediaContent(),
    'via.me': ViameMediaContent(),
    'flic.kr': FlickrMediaContent(),
}
