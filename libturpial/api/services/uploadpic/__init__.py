# -*- coding: utf-8 -*-

"""A list containing all upload pic services"""
#
# Author: Andrea Stagi (4ndreaSt4gi)

from libturpial.api.services.uploadpic.yfrog import YfrogUploader
from libturpial.api.services.uploadpic.twitpic import TwitpicPicUploader

PIC_SERVICES = {
    'twitpic': TwitpicPicUploader(),
    'yfrog': YfrogUploader(),
}
