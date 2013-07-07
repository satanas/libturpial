# -*- coding: utf-8 -*-

class List:
    """
    This class handles the information about a user list. It receives the
    *id_*, the *user* who owns it, the *name* (also known as slug), the *title*
    or caption, the number of *suscribers*, it *description* and the units
    used for plural and singular: *singular_unit*, *plural_unit*.

    :ivar id_: List id
    :ivar user: User that owns the list
    :ivar slug: List name
    :ivar title: List title
    :ivar suscribers: Suscribed users (count)
    :ivar description: List description
    :ivar single_unit: Singularized unit ('tweet' for example)
    :ivar plural_unit: Pluralized unit ('tweet' for example)
    """
    def __init__(self):
        self.id_ = None
        self.user = None
        self.slug = None
        self.title = None
        self.suscribers = None
        self.description = None
        self.single_unit = None
        self.plural_unit = None

    def __repr__(self):
        return "libturpial.api.models.List %" % (self.slug)
