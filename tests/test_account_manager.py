import pytest

from libturpial.exceptions import *
from libturpial.api.models.account import Account
from libturpial.config import AppConfig, AccountConfig
from libturpial.api.managers.accountmanager import AccountManager

class TestAccountManager:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        config = AppConfig()
        self.account = Account.new("twitter", "foo")
        self.accman = AccountManager(config, load=False)
        monkeypatch.setattr(Account, "load", lambda x: account)
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

    def test_load(self, monkeypatch):
        monkeypatch.setattr(Account, "load", lambda x: self.account)
        assert self.accman.load(self.account.id_) == self.account.id_


    def test_register(self, monkeypatch):
        monkeypatch.setattr(self.account, "is_authenticated", lambda: False)

        with pytest.raises(AccountNotAuthenticated):
            self.accman.register(self.account)

        monkeypatch.setattr(self.account, "is_authenticated", lambda: True)

        monkeypatch.setattr(self.account, "save", lambda: None)
        monkeypatch.setattr(self.accman, "load", lambda x: None)
        response = self.accman.register(self.account)
        assert response == "foo-twitter"

        monkeypatch.setattr(self.accman, '_AccountManager__accounts', self.account.id_)
        with pytest.raises(AccountAlreadyRegistered):
            self.accman.register(self.account)

    def test_unregister(self, monkeypatch):
        response = self.accman.unregister('foo-twitter', False)
        assert response == None

        monkeypatch.setattr(self.account, 'purge_config', lambda: None)
        monkeypatch.setattr(self.accman, '_AccountManager__accounts', {self.account.id_: self.account})

        response = self.accman.unregister(self.account.id_, delete_all=True)
        assert response == self.account.id_

    def test_get(self, monkeypatch):
        monkeypatch.setattr(self.accman, '_AccountManager__accounts', {self.account.id_: self.account})
        monkeypatch.setattr(self.accman, 'load', lambda x: None)

        account = self.accman.get('foo-twitter')
        assert isinstance(account, Account)
        assert account.id_ == 'foo-twitter'

        with pytest.raises(KeyError):
            account = self.accman.get('bar-twitter')

    def test_list(self, monkeypatch):
        account2 = Account.new("twitter", "bar")
        accounts = {self.account.id_: self.account, 'bar-twitter': account2}
        monkeypatch.setattr(self.accman, '_AccountManager__accounts', accounts)
        assert self.accman.list() == ['bar-twitter', 'foo-twitter']

    def test_accounts(self, monkeypatch):
        account2 = Account.new("twitter", "bar")
        accounts = {self.account.id_: self.account, 'bar-twitter': account2}
        monkeypatch.setattr(self.accman, '_AccountManager__accounts', accounts)
        assert account2 in self.accman.accounts()

