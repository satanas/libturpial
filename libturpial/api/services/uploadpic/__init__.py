# -*- coding: utf-8 -*-

"""A list containing all upload pic services"""
#
# Author: Andrea Stagi (4ndreaSt4gi)

from libturpial.api.services.uploadpic.yfrog import YfrogUploader
from libturpial.api.services.uploadpic.imgur import ImgurUploader
from libturpial.api.services.uploadpic.imgly import ImglyUploader
from libturpial.api.services.uploadpic.twitgoo import TwitgooUploader
from libturpial.api.services.uploadpic.twitpic import TwitpicUploader
from libturpial.api.services.uploadpic.lockerz import LockerzUploader
from libturpial.api.services.uploadpic.posterous import PosterousUploader
from libturpial.api.services.uploadpic.mobypicture import MobypictureUploader


PIC_SERVICES = {
    'lockerz': LockerzUploader(),
    'yfrog': YfrogUploader(),
    'twitpic': TwitpicUploader(),
    'img.ly': ImglyUploader(),
    'imgur': ImgurUploader(),
    'mobypicture': MobypictureUploader(),
    'posterous': PosterousUploader(),
    'twitgoo': TwitgooUploader(),
}
