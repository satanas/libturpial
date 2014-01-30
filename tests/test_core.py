import pytest

from libturpial.api.core import Core
from libturpial.api.models.list import List
from libturpial.api.models.column import Column
from libturpial.api.models.account import Account

class TestCore:
    @classmethod
    def setup_class(self):
        self.core = Core()

    @classmethod
    def teardown_class(self):
        pass

    def test_core_is_a_valid_instance(self):
        assert isinstance(self.core, Core)

    def test_local_variables(self):
        assert self.core.config != None
        assert self.core.accman != None
        assert self.core.column_manager != None

    def test_list_methods(self):
        accounts = self.core.list_accounts()
        assert isinstance(accounts, list)
        for item in accounts:
            assert isinstance(item, str)

        protocols = self.core.list_protocols()
        assert isinstance(protocols, list)
        for item in protocols:
            assert isinstance(item, str)

        filters = self.core.list_filters()
        assert isinstance(filters, list)
        for item in filters:
            assert isinstance(item, str)

    @pytest.fixture(autouse=True)
    def test_registering(self, monkeypatch):
        dummy = Account('twitter')
        monkeypatch.setattr(self.core.accman, "register", lambda x: "dummy-twitter")
        monkeypatch.setattr(self.core.column_manager, "register", lambda x: "dummy-twitter-column1")

        result = self.core.register_account(dummy)
        assert isinstance(result, str)

        result = self.core.register_column("dummy-twitter-column1")
        assert isinstance(result, str)

    @pytest.fixture(autouse=True)
    def test_unregistering(self, monkeypatch):
        monkeypatch.setattr(self.core.accman, "unregister", lambda x,y: "dummy-twitter")
        monkeypatch.setattr(self.core.column_manager, "unregister", lambda x: "dummy-twitter-column1")

        result = self.core.unregister_account("dummy-twitter")
        assert isinstance(result, str)

        result = self.core.unregister_column("dummy-twitter-column1")
        assert isinstance(result, str)

    def test_all_columns(self):
        columns = self.core.all_columns()
        assert isinstance(columns, dict)
        for key, value in columns.iteritems():
            assert isinstance(value, list)
            for col in value:
                assert (isinstance(col, Column) or isinstance(col, List))

    def test_available_columns(self):
        columns = self.core.available_columns()
        assert isinstance(columns, dict)
        for key, value in columns.iteritems():
            assert isinstance(value, list)
            for col in value:
                assert (isinstance(col, Column) or isinstance(col, List))

    def test_registered_columns(self):
        columns = self.core.registered_columns()
        assert isinstance(columns, dict)
        for key, value in columns.iteritems():
            assert isinstance(value, list)
            for col in value:
                assert (isinstance(col, Column) or isinstance(col, List))

    def test_registered_columns_by_order(self):
        columns = self.core.registered_columns_by_order()
        assert isinstance(columns, list)
        for col in columns:
            assert (isinstance(col, Column) or isinstance(col, List))

    def test_registered_accounts(self):
        accounts = self.core.registered_accounts()
        assert isinstance(accounts, list)
        for acc in accounts:
            assert isinstance(acc, Account)

