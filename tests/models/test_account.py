import os
import pytest
import __builtin__

from libturpial.config import AccountConfig
from libturpial.api.models.list import List
from libturpial.api.models.column import Column
from libturpial.api.models.profile import Profile
from libturpial.api.models.account import Account
from libturpial.lib.protocols.twitter.twitter import Main as MainTwitter
from libturpial.lib.protocols.identica.identica import Main as MainIdentica
from libturpial.exceptions import AccountNotAuthenticated, ErrorLoadingAccount

class DummyAccount:
    def __init__(self, arg1, arg2):
        self.id_ = arg1
        self.config = None
    def setup_user_credentials(self, arg1, arg2, arg3):
        pass
    def fetch(self):
        pass
    @staticmethod
    def new(arg1, arg2):
        return DummyAccount(arg1, arg2)

class DummyProtocol:
    def __init__(self):
        self.profile = Profile()
        self.friends = []
    def request_token(self):
        return 'token'
    def authorize_token(self, pin):
        return self.profile
    def verify_credentials(self):
        return self.profile
    def get_lists(self, arg):
        return []
    def get_following(self, only_id):
        return self.friends
    def update_profile(self, fullname, url, bio, location):
        self.profile.fullname = fullname
        self.profile.url = url
        self.profile.bio = bio
        self.profile.location = location
        return self.profile

class DummyConfig:
    def __init__(self, arg=None):
        self.cache_size = 0
    @staticmethod
    def exists(value):
        return False
    def save_oauth_credentials(self, arg1, arg2):
        pass
    def load_oauth_credentials(self):
        pass
    def dismiss(self):
        pass
    def delete_cache(self):
        pass
    def calculate_cache_size(self):
        return self.cache_size

class DummyToken:
    def __init__(self):
        self.key = '123'
        self.secret = '456'

class DummyProfile:
    def is_me(self):
        return True

class DummyFileHandler:
    def __init__(self, array=None):
        if array:
            self.array = array
        else:
            self.array = []
    def __iter__(self):
        return iter(self.array)
    def close(self):
        pass
    def write(self, argument):
        pass

class TestAccount:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        self.account = Account('twitter', 'foo')

    def test_init(self):
        account = Account('twitter')
        assert isinstance(account.protocol, MainTwitter)

        account = Account('identica')
        assert isinstance(account.protocol, MainIdentica)

    def test_repr(self):
        assert str(self.account) == "libturpial.api.models.Account foo-twitter"

    def test_new(self):
        account = Account.new('twitter', 'foo')
        assert isinstance(account, Account)

    def test_new_with_params(self, monkeypatch):
        monkeypatch.setattr('libturpial.api.models.account.Account', DummyAccount)

        account = Account.new_from_params('twitter', 'foo', '123', '456', '789')
        assert isinstance(account, DummyAccount)

    def test_load(self, monkeypatch):
        monkeypatch.setattr('libturpial.config.AccountConfig', DummyConfig)

        with pytest.raises(ErrorLoadingAccount):
            Account.load('foo-twitter')

        # Monkeypatching Account.exists
        monkeypatch.setattr(os.path, 'isfile', lambda x: True)

        # Monkeypatching AppConfig create
        monkeypatch.setattr(os, 'makedirs', lambda x: None)
        monkeypatch.setattr(__builtin__, 'open', lambda x, y: DummyFileHandler())
        monkeypatch.setattr(AccountConfig, 'create', lambda: None)
        monkeypatch.setattr(AccountConfig, 'load_oauth_credentials', lambda x: ('123', '456'))

        monkeypatch.setattr('libturpial.api.models.account.Account', DummyAccount)
        Account.load('foo-twitter')

    def test_request_oauth_access(self, monkeypatch):
        monkeypatch.setattr(self.account, 'protocol', DummyProtocol())

        assert self.account.request_oauth_access() == 'token'

    def test_authorize_oauth_access(self, monkeypatch):
        protocol = DummyProtocol()
        protocol.profile.username = 'foo'
        monkeypatch.setattr(self.account, 'protocol', protocol)

        self.account.authorize_oauth_access('123')
        assert self.account.profile.username == 'foo'

    def test_save(self, monkeypatch):
        monkeypatch.setattr(self.account, 'is_authenticated', lambda: False)

        with pytest.raises(AccountNotAuthenticated):
            self.account.save()

        # Monkeypatching AppConfig create
        monkeypatch.setattr(os, 'makedirs', lambda x: None)
        monkeypatch.setattr(AccountConfig, 'create', lambda x: None)
        monkeypatch.setattr(AccountConfig, 'load', lambda x: None)
        monkeypatch.setattr(AccountConfig, 'load_failsafe', lambda x: None)
        monkeypatch.setattr(AccountConfig, 'exists', lambda x, y: True)
        monkeypatch.setattr(AccountConfig, 'save_oauth_credentials', lambda x, y, z: None)

        monkeypatch.setattr(self.account, 'is_authenticated', lambda: True)
        monkeypatch.setattr(self.account, 'get_oauth_token', lambda: DummyToken())

        # TODO: How to test that this works?
        assert self.account.save() == None

    def test_fetch(self, monkeypatch):
        monkeypatch.setattr(self.account, 'protocol', DummyProtocol())

        self.account.fetch()
        assert len(self.account.columns) == 5
        for col in self.account.columns:
            assert isinstance(col, Column)

    def test_fetch_friends(self, monkeypatch):
        protocol = DummyProtocol()
        protocol.profile.username = 'foo'
        protocol.friends = ['bar', 'baz']
        monkeypatch.setattr(self.account, 'protocol', protocol)

        friends = self.account.fetch_friends()
        assert friends == ['bar', 'baz']

    def test_get_column(self, monkeypatch):
        monkeypatch.setattr(self.account, 'columns', [])
        assert self.account.get_columns() == []

    def test_get_list_id(self, monkeypatch):
        monkeypatch.setattr(self.account, 'lists', None)

        assert self.account.get_list_id('bla') == None

        l1 = List()
        l1.id_ = '123'
        l1.slug = 'foolist'
        lists = [l1]
        monkeypatch.setattr(self.account, 'lists', lists)

        assert self.account.get_list_id('foolist') == '123'
        assert self.account.get_list_id('ble') == None

    def test_purge_config(self, monkeypatch):
        monkeypatch.setattr(self.account, 'config', DummyConfig('bla'))

        # TODO: How to test that this works?
        assert self.account.purge_config() == None

    def test_delete_cache(self, monkeypatch):
        monkeypatch.setattr(self.account, 'config', DummyConfig('bla'))

        # TODO: How to test that this works?
        assert self.account.delete_cache() == None

    def test_get_cache_size(self, monkeypatch):
        config = DummyConfig('bla')
        config.cache_size = 1000

        monkeypatch.setattr(self.account, 'config', config)

        assert self.account.get_cache_size() == 1000

    def test_is_authenticated(self, monkeypatch):
        monkeypatch.setattr(self.account, 'profile', None)
        monkeypatch.setattr(self.account, 'id_', None)

        assert self.account.is_authenticated() == False

        monkeypatch.setattr(self.account, 'id_', '123')
        assert self.account.is_authenticated() == False

        profile = Profile()
        monkeypatch.setattr(self.account, 'profile', profile)
        monkeypatch.setattr(self.account, 'id_', None)
        assert self.account.is_authenticated() == False

        monkeypatch.setattr(self.account, 'id_', '123')
        assert self.account.is_authenticated() == True

    def test_update_profile(self, monkeypatch):
        monkeypatch.setattr(self.account, 'protocol', DummyProtocol())

        profile = self.account.update_profile(fullname='foo')
        assert profile.fullname == 'foo'
        assert profile.url == None
        assert profile.bio == None
        assert profile.location == None

        profile = self.account.update_profile(fullname='bar', url='http://example.com')
        assert profile.fullname == 'bar'
        assert profile.url == 'http://example.com'
        assert profile.bio == None
        assert profile.location == None

        profile = self.account.update_profile(fullname='baz', url='http://hello.com',
                bio='Lorem Ipsum')
        assert profile.fullname == 'baz'
        assert profile.url == 'http://hello.com'
        assert profile.bio == 'Lorem Ipsum'
        assert profile.location == None

        profile = self.account.update_profile(fullname='qux', url='http://bye.com',
                bio='Lorem', location='here')
        assert profile.fullname == 'qux'
        assert profile.url == 'http://bye.com'
        assert profile.bio == 'Lorem'
        assert profile.location == 'here'

    def test_get_attr(self, monkeypatch):
        monkeypatch.setattr(self.account, 'profile', DummyProfile())
        monkeypatch.setattr(self.account, 'protocol', DummyProtocol())

        assert self.account.is_me() == True
        assert self.account.request_token() == 'token'

        with pytest.raises(AttributeError):
            self.account.foobar()
