# -*- coding: utf-8 -*-


class Column:
    """
    This model represents a column that holds
    :class:`libturpial.api.models.status.Status` objects. You need to specify
    to what *account_id* are they associated, as well as the column *slug*.
    Available column slugs are available in
    :class:`libturpial.common.ColumnType`.

    :ivar id_: Column id (for example: "johndoe-twitter-timeline")
    :ivar slug: Column slug
    :ivar account_id: id of account associated to the column
    :ivar size: max number of statuses that this column can hold
    :ivar singular_unit: unit used to identify one status (e.g: 'tweet')
    :ivar plural_unit: unit used to identify more than one status
          (e.g: 'tweets')
    """
    def __init__(self, account_id, slug, singular_unit='tweet',
                 plural_unit='tweets'):
        self.size = 0
        self.id_ = "%s-%s" % (account_id, slug)  # username-protocol-column
        self.slug = slug
        self.account_id = account_id
        self.updating = False
        self.singular_unit = singular_unit
        self.plural_unit = plural_unit

    def __repr__(self):
        return "libturpial.api.models.Column %s" % (self.id_)
