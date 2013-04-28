# -*- coding: utf-8 -*-

class Column:
    """
    This model represents a column that holds statuses. To instanciate it you
    need to specify it *_type*, *the account_id* it iss associated to, the
    *protocol_id* and it *name*
    """
    def __init__(self, type_, name, account_id, protocol_id,
            singular_unit='tweet', plural_unit='tweets'):
        self.size = 0
        self.type_ = type_  # If id_ == "" is not registered. Otherwise, registered
        self.name = name
        self.account_id = account_id  # username-protocol_id
        self.protocol_id = protocol_id
        self.updating = False
        self.slug = "%s-%s" % (self.account_id, self.column_name)
        self.singular_unit = singular_unit
        self.plural_unit = plural_unit
