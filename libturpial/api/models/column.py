# -*- coding: utf-8 -*-

class Column:
    """
    This model represents a column that holds statuses. To instanciate it you
    need to specify it *type_*, *the account_id* it is associated to, the
    *protocol_id* and it *name*
    """
    # TODO: Update doc. column_id is something like: satanas82-twitter-timeline
    def __init__(self, account_id, type_, singular_unit='tweet',
            plural_unit='tweets'):
        self.size = 0
        self.id_ = "%s-%s" % (account_id, type_) # username-protocol-column
        self.type_ = type_
        self.account_id = account_id
        self.updating = False
        self.singular_unit = singular_unit
        self.plural_unit = plural_unit
