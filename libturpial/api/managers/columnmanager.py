# -*- coding: utf-8 -*-

from libturpial.api.models.column import Column
from libturpial.common import get_account_id_from, get_column_type_from

class ColumnManager:
    def __init__(self, config):
        self.config = config
        self.__load_registered()

    def __len__(self):
        return len(self.__registered_columns)

    def __iter__(self):
        return self.__registered_columns.iteritems()

    def __load_registered(self):
        self.__registered_columns = {}

        for column_id in self.config.get_stored_columns():
            account_id = get_account_id_from(column_id)
            column_type = get_column_type_from(column_id)
            if not self.__registered_columns.has_key(account_id):
                self.__registered_columns[account_id] = []
            self.__registered_columns[account_id].append(Column(account_id, column_type))

    def __count(self):
        count = 0
        for account_id, columns in self.__registered_columns.iteritems():
            for col in columns:
                count += 1
        return count

    def register(self, column_id):
        for account_id, columns in self.__registered_columns.iteritems():
            for col in columns:
                if col.id_ == column_id:
                    return None

        count = self.__count() + 1
        key = "column%s" % count
        self.config.write('Columns', key, column_id)

        self.__load_registered()
        return column_id

    def unregister(self, column_id):
        index = 0
        to_store = {}
        for account_id, columns in self.__registered_columns.iteritems():
            for col in columns:
                if col.id_ != column_id:
                    index += 1
                    key = "column%s" % index
                    to_store[key] = col.id_
        self.config.write_section('Columns', to_store)

        self.__load_registered()
        return column_id

    def columns(self):
        return self.__registered_columns

    def is_registered(self, column_id):
        for account_id, columns in self.__registered_columns.iteritems():
            for col in columns:
                if col.id_ == column_id:
                    return True
        return False

