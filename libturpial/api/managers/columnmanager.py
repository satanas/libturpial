# -*- coding: utf-8 -*-

from libturpial.api.models.column import Column
from libturpial.exceptions import ColumnAlreadyRegistered
from libturpial.common import get_account_id_from, get_column_slug_from


class ColumnManager:
    """
    This class has methods to manage columns. You can register new columns,
    load and unregister existing columns.

    This manager can be iterated and each element will have a list of columns
    per account. For example:

    >>> from libturpial.config import AppConfig
    >>> config = AppConfig()
    >>> column_manager = ColumnManager(config)
    >>> [column for column in column_manager.columns()]

    """
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
            column_slug = get_column_slug_from(column_id)
            if account_id not in self.__registered_columns:
                self.__registered_columns[account_id] = []
            self.__registered_columns[account_id].append(Column(account_id,
                                                                column_slug))

    def __count(self):
        count = 0
        for account_id, columns in self.__registered_columns.iteritems():
            for col in columns:
                count += 1
        return count

    def register(self, column_id):
        """
        Register a new column identified by *column_id*. If the column is
        already registered a
        :class:`libturpial.exceptions.ColumnAlreadyRegistered` exception will
        raise. Return the id of the column registered on success
        """
        for account_id, columns in self.__registered_columns.iteritems():
            for col in columns:
                if col.id_ == column_id:
                    raise ColumnAlreadyRegistered

        count = self.__count() + 1
        key = "column%s" % count
        self.config.write('Columns', key, column_id)

        self.__load_registered()
        return column_id

    def unregister(self, column_id):
        """
        Remove the column identified by *column_id* from memory. Return the id
        of the unregistered column.
        """
        index = 0
        to_store = {}
        ordered_columns = self.columns_by_order()
        columns = [col for col in ordered_columns if col.id_ != column_id]
        for col in columns:
            index += 1
            key = "column%s" % index
            to_store[key] = col.id_
        self.config.write_section('Columns', to_store)

        self.__load_registered()
        return column_id

    def get(self, column_id):
        """
        Obtain the column identified by *column_id* and return a 
        :class:`libturpial.api.models.column.Column` object on success. None
        otherwise.
        """
        for account_id, columns in self.__registered_columns.iteritems():
            for col in columns:
                if col.id_ == column_id:
                    return col
        return None

    def columns(self):
        """
        Return a dict where each key represents an account_id and it value is
        a list of :class:`libturpial.api.models.column.Column` objects
        with all the columns registered.

        For example:

        >>> from libturpial.config import AppConfig
        >>> config = AppConfig()
        >>> column_manager = ColumnManager(config)
        >>> column_manager.columns()
        """
        return self.__registered_columns

    def columns_by_order(self):
        i = 1
        columns = []
        while True:
            column_num = "column%s" % i
            column_id = self.config.read('Columns', column_num)
            if column_id:
                account_id = get_account_id_from(column_id)
                column_slug = get_column_slug_from(column_id)
                columns.append(Column(account_id, column_slug))
                i += 1
            else:
                break
        return columns

    def is_registered(self, column_id):
        """
        Return `True` if column identified by *column_id* is registered.
        `False` otherwise.
        """
        for account_id, columns in self.__registered_columns.iteritems():
            for col in columns:
                if col.id_ == column_id:
                    return True
        return False
