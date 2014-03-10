# -*- coding: utf-8 -*-

"""A list containing all upload pic services"""
#
# Author: Andrea Stagi (4ndreaSt4gi)

from .yfrog import YfrogUploader
from .twitpic import TwitpicUploader
from .imgly import ImglyUploader
from .mobypicture import MobypictureUploader
from .twitgoo import TwitgooUploader


UPLOAD_MEDIA_SERVICES = {
    'yfrog': YfrogUploader(),
    'twitpic': TwitpicUploader(),
    'img.ly': ImglyUploader(),
    'mobypicture': MobypictureUploader(),
    'twitgoo': TwitgooUploader(),
}
