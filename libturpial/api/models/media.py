# -*- coding: utf-8 -*-

import os
import tempfile


class Media(object):
    """
    This class represents a media object (image, video or map) that can be
    rendered on the UI. *type_* could be
    :py:attr:`libturpial.api.models.media.IMAGE`,
    :py:attr:`libturpial.api.models.media.VIDEO` or
    :py:attr:`libturpial.api.models.media.MAP`, *name* is the filename and
    *content* holds the binary data of the media. If *path* is `None` a
    temporary path will be created using the filename. *info* stores any
    additional information about the resource.
    """

    IMAGE = 0
    VIDEO = 1
    MAP = 2

    def __init__(self, type_, name, content, path=None, info=None):
        self.type_ = type_
        self.info = info
        self.name = self.__sanitize_name(name)
        if path is None:
            self.path = os.path.join(tempfile.gettempdir(), self.name)
        else:
            self.path = path
        if content:
            self.content = content
            self.save_content()

    def __sanitize_name(self, name):
        name = name.replace('http://', '')
        name = name.replace('https://', '')
        name = name.replace(':', '.')
        name = name.replace('/', '_')
        if name.find('.jpg') < 0 and name.find('.jpeg') < 0 and \
                name.find('.png') < 0 and name.find('.gif') < 0:
            name = "%s.jpg" % (name)
        return name

    @staticmethod
    def new_image(name, content, path=None, info=None):
        """
        Create an image media
        """
        return Media(Media.IMAGE, name, content, path, info)

    # TODO: Return True when success?
    def save_content(self):
        """
        Saves the content of the media in the path specified.
        """
        try:
            fd = open(self.path, 'wb')
            fd.write(self.content)
            fd.close()
        except KeyError:
            pass

    def is_video(self):
        """
        Returns `True` if the media is a video
        """
        return self.type_ == self.VIDEO

    def is_image(self):
        """
        Returns `True` if the media is an image
        """
        return self.type_ == self.IMAGE

    def is_map(self):
        """
        Returns `True` if the media is a map
        """
        return self.type_ == self.MAP
