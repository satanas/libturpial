# -*- coding: utf-8 -*-

import os
import tempfile

IMAGE = 0
VIDEO = 1
MAP = 2


class Media(object):
    """
    This class models a media object (image, video or map) that can be rendered
    on the UI. *type_* could be :var:`libturpial.api.models.media.IMAGE`,
    :var:`libturpial.api.models.media.VIDEO` or
    :var:`libturpial.api.models.media.MAP`, *name* is the URI name and
    *content* is the binary content of the media. If *path* is **None** a
    temporary path will be created and *info* holds any additional information
    about the resource.
    """

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
        """
        Saves the content of the media in the path specified on init.
        """
        try:
            fd = open(self.path, 'wb')
            fd.write(self.content)
            fd.close()
        except KeyError:
            pass

    def is_video(self):
        """
        Returns **True** if the media is a video
        """
        return self.type_ == VIDEO

    def is_image(self):
        """
        Returns **True** if the media is an image
        """
        return self.type_ == IMAGE

    def is_map(self):
        """
        Returns **True** if the media is a map
        """
        return self.type_ == MAP
