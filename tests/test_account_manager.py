import pytest

from libturpial.exceptions import *
from libturpial.config import AppConfig
from libturpial.api.models.account import Account
from libturpial.api.managers.accountmanager import AccountManager


class TestAccountManager:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        config = AppConfig()
        self.account = Account.new("twitter", "foo")
        self.accman = AccountManager(config, load=False)
        #self.core = Core(load_accounts=False)
        #self.account = Account.new("twitter", "dummy")
        #monkeypatch.setattr(self.core.accman, "get", lambda x: self.account)

    def test_init(self, monkeypatch):
        config = AppConfig()
        accman = AccountManager(config, load=False)
        assert len(accman) == 0

        # TODO: Monkeypatch class method load in Account
        #monkeypatch.setattr(config, "get_stored_accounts", lambda: ['foo-twitter'])
        #monkeypatch.setattr(Account, "load", lambda x: account)
        #accman = AccountManager(config)

    def test_register(self, monkeypatch):
        monkeypatch.setattr(self.account, "is_authenticated", lambda: False)

        with pytest.raises(AccountNotAuthenticated):
            self.accman.register(self.account)

        monkeypatch.setattr(self.account, "is_authenticated", lambda: True)
        monkeypatch.setattr(self.account, "save", lambda: None)
        monkeypatch.setattr(self.accman, "load", lambda x: None)
        response = self.accman.register(self.account)
        assert response == "foo-twitter"

        # TODO: Monkeypatch class method load in Account and test exception

