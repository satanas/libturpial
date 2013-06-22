# -*- coding: utf-8 -*-

from libturpial.api.models.column import Column
from libturpial.common import get_account_id_from, get_column_name_from

class ColumnManager:
    def __init__(self, config):
        self.config = config
        self.__load_registered()

    def __len__(self):
        return len(self.__registered_columns)

    def __iter__(self):
        return self.__registered_columns.iteritems()

    def __load_registered(self):
        self.__registered_columns = []

        for column_id in self.config.get_stored_columns():
            account_id = get_account_id_from(column_id)
            column_name = get_column_name_from(column_id)
            self.__registered_columns.append(Column(account_id, column_name))

    def register(self, column_id):
        for col in self.__registered_columns:
            if col.id_ == column_id:
                return None

        count = len(self.__registered_columns) + 1
        key = "column%s" % count
        self.config.write('Columns', key, column_id)

        self.__load_registered()
        return col.id_

    def unregister(self, column_id):
        index = 0
        to_store = {}
        for col in self.__registered_columns:
            if col.id_ != column_id:
                index += 1
                key = "column%s" % index
                to_store[key] = col.id_
        self.config.write_section('Columns', to_store)

        self.__load_registered()
        return column_id
