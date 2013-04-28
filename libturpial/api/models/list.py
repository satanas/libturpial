# -*- coding: utf-8 -*-

class List:
    """
    This class handles the information about a user list. It receives the
    *id_*, the *user* who owns it, the *name* (also known as slug), the *title*
    or caption, the number of *suscribers*, it *description* and the units
    used for plural and singular: *singular_unit*, *plural_unit*.
    """
    def __init__(self):
        self.id_ = None
        self.user = None
        self.name = None
        self.title = None
        self.suscribers = None
        self.description = None
        self.single_unit = None
        self.plural_unit = None
