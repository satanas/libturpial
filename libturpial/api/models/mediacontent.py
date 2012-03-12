# -*- coding: utf-8 -*-

""" Module to handle media content objects """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 11, 2012

import os
import tempfile

IMAGE_CONTENT = 0
VIDEO_CONTENT = 1

class MediaContent(object):
    def __init__(self, type_, name, content):
        self.type_ = type_
        self.name = name.replace("/", "%")
        self.content = content
        self.path = os.path.join(tempfile.gettempdir(), self.name)

    def save_content(self):
        try:
            fd = open(self.path, 'wb')
            fd.write(self.content)
            fd.close()
        except KeyError:
            pass

    def is_video(self):
        if self.type_ == VIDEO_CONTENT:
            return True
        return False

    def is_image(self):
        if self.type_ == IMAGE_CONTENT:
            return True
        return False
