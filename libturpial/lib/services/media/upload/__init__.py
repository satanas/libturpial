# -*- coding: utf-8 -*-

"""A list containing all upload pic services"""
#
# Author: Andrea Stagi (4ndreaSt4gi)

from libturpial.lib.services.media.upload.yfrog import YfrogUploader
from libturpial.lib.services.media.upload.twitpic import TwitpicUploader
from libturpial.lib.services.media.upload.imgly import ImglyUploader
from libturpial.lib.services.media.upload.mobypicture import MobypictureUploader
from libturpial.lib.services.media.upload.twitgoo import TwitgooUploader


UPLOAD_MEDIA_SERVICES = {
    'pic.twitter.com': None,
    'yfrog': YfrogUploader(),
    'twitpic': TwitpicUploader(),
    'img.ly': ImglyUploader(),
    'mobypicture': MobypictureUploader(),
    'twitgoo': TwitgooUploader(),
}
