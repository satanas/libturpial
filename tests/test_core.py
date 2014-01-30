import pytest

from libturpial.api.core import Core
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
        assert isinstance(self.core.list_accounts(), list)
        assert isinstance(self.core.list_protocols(), list)
        assert isinstance(self.core.list_filters(), list)

    @pytest.fixture(autouse=True)
    def test_registering(self, monkeypatch):
        dummy = Account('twitter')
        monkeypatch.setattr(self.core.accman, "register", "dummy-twitter")

        result = self.core.register_account(dummy)
        assert isinstance(result, str)

