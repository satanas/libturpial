# -*- coding: utf-8 -*-

""" Module to handle media content objects """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 11, 2012

import os
import tempfile

IMAGE_CONTENT = 0
VIDEO_CONTENT = 1
MAP_CONTENT = 2

class MediaContent(object):
    def __init__(self, type_, name, content, path=None, info=None):
        self.type_ = type_
        self.name = name.replace("/", "_")
        self.name = self.name.replace(":", ".")
        self.content = content
        if path is None:
            self.path = os.path.join(tempfile.gettempdir(), self.name)
        else:
            self.path = path
        self.info = info

    def save_content(self):
        try:
            fd = open(self.path, 'wb')
            fd.write(self.content)
            fd.close()
        except KeyError:
            pass

    def is_video(self):
        return self.type_ == VIDEO_CONTENT

    def is_image(self):
        return self.type_ == IMAGE_CONTENT

    def is_map(self):
        return self.type_ == MAP_CONTENT

