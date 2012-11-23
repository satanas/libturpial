# -*- coding: utf-8 -*-

"""A list containing all upload pic services"""
#
# Author: Andrea Stagi (4ndreaSt4gi)

from libturpial.api.services.uploadpic.yfrog import YfrogUploader
from libturpial.api.services.uploadpic.imgly import ImglyUploader
from libturpial.api.services.uploadpic.twitpic import TwitpicUploader
from libturpial.api.services.uploadpic.mobypicture import MobypictureUploader


PIC_SERVICES = {
    'twitpic': TwitpicUploader(),
    'yfrog': YfrogUploader(),
    'img.ly': ImglyUploader(),
    'mobypicture': MobypictureUploader(),
}
