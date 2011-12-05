# -*- coding: utf-8 -*-

""" Module to represent user columns """
#
# Author: Wil Alvarez (aka Satanas)
# Nov 25, 2011


class Column:
    def __init__(self, id_, acc_id=None, pt_id=None, col_name=None):
        self.id_ = id_ # If id_ == "" is not registered. Otherwise, registered
        self.account_id = acc_id # username-protocol_id
        self.protocol_id = pt_id
        self.column_name = col_name
        self.updating = False
