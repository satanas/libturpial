import pytest

from libturpial.config import AppConfig
from libturpial.api.core import Core
from libturpial.api.models.list import List
from libturpial.api.models.status import Status
from libturpial.api.models.column import Column
from libturpial.api.models.profile import Profile
from libturpial.api.models.account import Account
from libturpial.api.managers.columnmanager import ColumnManager
from libturpial.api.managers.accountmanager import AccountManager

class TestCore:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        self.core = Core(load_accounts=False)
        self.account = Account.new("twitter")
        monkeypatch.setattr(self.core.accman, "get", lambda x: self.account)

    @classmethod
    def teardown_class(self):
        pass

    def test_core_is_a_valid_instance(self):
        assert isinstance(self.core, Core)

    def test_local_variables(self):
        assert self.core.config != None
        assert isinstance(self.core.config, AppConfig)
        assert self.core.accman != None
        assert isinstance(self.core.accman, AccountManager)
        assert self.core.column_manager != None
        assert isinstance(self.core.column_manager, ColumnManager)

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

    @pytest.fixture(autouse=True)
    def test_get_single_column(self, monkeypatch):
        dummy = Column("dummy-twitter", "foo")
        monkeypatch.setattr(self.core.column_manager, "get", lambda x: dummy)

        column = self.core.get_single_column("dummy-twitter-column")
        assert isinstance(column, Column)

    def test_get_single_account(self):
        account = self.core.get_single_account("dummy-twitter")
        assert isinstance(account, Account)

    @pytest.fixture(autouse=True)
    def test_get_column_statuses(self, monkeypatch):
        status = Status()
        result = [status]

        status.id_ = "123"
        monkeypatch.setattr(self.account, "get_timeline", lambda x, y: result)
        response = self.core.get_column_statuses("dummy-twitter", "timeline")
        assert isinstance(response, list)
        assert response[0].id_, "123"

        status.id_ = "124"
        monkeypatch.setattr(self.account, "get_replies", lambda x, y: result)
        response = self.core.get_column_statuses("dummy-twitter", "replies")
        assert isinstance(response, list)
        assert response[0].id_, "124"

        status.id_ = "125"
        monkeypatch.setattr(self.account, "get_directs", lambda x, y: result)
        response = self.core.get_column_statuses("dummy-twitter", "directs")
        assert isinstance(response, list)
        assert response[0].id_, "125"

        status.id_ = "126"
        monkeypatch.setattr(self.account, "get_favorites", lambda x: result)
        response = self.core.get_column_statuses("dummy-twitter", "favorites")
        assert isinstance(response, list)
        assert response[0].id_, "126"

        list_ = List()
        list_.id_ = "666"
        monkeypatch.setattr(self.account, "get_list_id", lambda x: list_)
        status.id_ = "127"
        monkeypatch.setattr(self.account, "get_list_statuses", lambda x, y, z: result)
        response = self.core.get_column_statuses("dummy-twitter", "my-list")
        assert isinstance(response, list)
        assert response[0].id_, "127"

    @pytest.fixture(autouse=True)
    def test_get_followers(self, monkeypatch):
        profile = Profile()
        profile.id_ = "dummy"
        result = [profile]

        monkeypatch.setattr(self.account, "get_followers", lambda x: result)

        response = self.core.get_followers("dummy-twitter")
        assert isinstance(response, list)
        assert response[0].id_, "dummy"

    @pytest.fixture(autouse=True)
    def test_get_following(self, monkeypatch):
        profile = Profile()
        profile.id_ = "dummy"
        result = [profile]

        monkeypatch.setattr(self.account, "get_following", lambda x: result)

        response = self.core.get_following("dummy-twitter")
        assert isinstance(response, list)
        assert response[0].id_, "dummy"

    @pytest.fixture(autouse=True)
    def test_get_all_friends_list(self, monkeypatch):
        account = Account.new("twitter")
        accounts = [account]
        profile = Profile()
        profile.username = "dummy"
        result = [profile]

        monkeypatch.setattr(self.core.accman, "accounts", lambda: accounts)
        monkeypatch.setattr(account, "get_following", lambda: result)

        friends = self.core.get_all_friends_list()
        assert isinstance(friends, list)
        assert friends[0], "dummy"

    def test_load_all_friends_list(self):
        result = self.core.load_all_friends_list()
        assert isinstance(result, list)
        for friend in result:
            assert isinstance(friend, str)


    @pytest.fixture(autouse=True)
    def test_get_user_profile(self, monkeypatch):
        profile = Profile()
        self.account.profile = profile
        result = [profile]

        monkeypatch.setattr(self.account, "get_profile", lambda x: profile)
        monkeypatch.setattr(self.account, "is_friend", lambda x: True)
        monkeypatch.setattr(self.core, "is_muted", lambda x: False)

        profile.id_ = "dummy"
        response = self.core.get_user_profile("dummy-twitter")
        assert isinstance(response, Profile)
        assert response.id_, "dummy"

        profile.id_ = "user"
        response = self.core.get_user_profile("dummy-twitter", "user")
        assert isinstance(response, Profile)
        assert response.id_, "user"
        assert response.followed_by, True
        assert not response.muted, True

    @pytest.fixture(autouse=True)
    def test_get_conversation(self, monkeypatch):
        status = Status()
        status.id_ = "321"
        conversation = [status]

        monkeypatch.setattr(self.account, "get_conversation", lambda x: conversation)

        response = self.core.get_conversation("dummy-twitter", "123")
        assert isinstance(response, list)
        assert isinstance(response[0], Status)
        assert response[0].id_, "321"





