import os
import pytest
import tempfile

from libturpial.exceptions import *
from libturpial.api.core import Core
from libturpial.config import AppConfig
from libturpial.config import AccountConfig
from libturpial.api.models.list import List
from libturpial.api.models.media import Media
from libturpial.api.models.trend import Trend
from libturpial.api.models.status import Status
from libturpial.api.models.column import Column
from libturpial.api.models.profile import Profile
from libturpial.api.models.account import Account
from libturpial.api.models.trend import TrendLocation
from libturpial.api.managers.columnmanager import ColumnManager
from libturpial.api.managers.accountmanager import AccountManager

class DummyConfig:
    def __init__(self):
        self.imgdir = "/path/to/ble"

class TestCore:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        self.acc_id = "dummy-twitter"
        self.core = Core(load_accounts=False)
        self.account = Account.new("twitter", "dummy")
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

    def test_registering(self, monkeypatch):
        dummy = Account('twitter')
        monkeypatch.setattr(self.core.accman, "register", lambda x: self.acc_id)
        monkeypatch.setattr(self.core.column_manager, "register", lambda x: "dummy-twitter-column1")

        result = self.core.register_account(dummy)
        assert isinstance(result, str)

        result = self.core.register_column("dummy-twitter-column1")
        assert isinstance(result, str)

    def test_unregistering(self, monkeypatch):
        monkeypatch.setattr(self.core.accman, "unregister", lambda x,y: self.acc_id)
        monkeypatch.setattr(self.core.column_manager, "unregister", lambda x: "dummy-twitter-column1")

        result = self.core.unregister_account(self.acc_id)
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

    def test_get_single_column(self, monkeypatch):
        dummy = Column(self.acc_id, "foo")
        monkeypatch.setattr(self.core.column_manager, "get", lambda x: dummy)

        column = self.core.get_single_column("dummy-twitter-column")
        assert isinstance(column, Column)

    def test_get_single_account(self):
        account = self.core.get_single_account(self.acc_id)
        assert isinstance(account, Account)

    def test_get_column_statuses(self, monkeypatch):
        status = Status()
        result = [status]

        status.id_ = "123"
        monkeypatch.setattr(self.account, "get_timeline", lambda x, y: result)
        response = self.core.get_column_statuses(self.acc_id, "timeline")
        assert isinstance(response, list)
        assert response[0].id_, "123"

        status.id_ = "124"
        monkeypatch.setattr(self.account, "get_replies", lambda x, y: result)
        response = self.core.get_column_statuses(self.acc_id, "replies")
        assert isinstance(response, list)
        assert response[0].id_, "124"

        status.id_ = "125"
        monkeypatch.setattr(self.account, "get_directs", lambda x, y: result)
        response = self.core.get_column_statuses(self.acc_id, "directs")
        assert isinstance(response, list)
        assert response[0].id_, "125"

        status.id_ = "126"
        monkeypatch.setattr(self.account, "get_favorites", lambda x: result)
        response = self.core.get_column_statuses(self.acc_id, "favorites")
        assert isinstance(response, list)
        assert response[0].id_, "126"

        list_ = List()
        list_.id_ = "666"
        monkeypatch.setattr(self.account, "get_list_id", lambda x: list_)
        status.id_ = "127"
        monkeypatch.setattr(self.account, "get_list_statuses", lambda x, y, z: result)
        response = self.core.get_column_statuses(self.acc_id, "my-list")
        assert isinstance(response, list)
        assert response[0].id_, "127"

    def test_get_followers(self, monkeypatch):
        profile = Profile()
        profile.id_ = "dummy"
        result = [profile]

        monkeypatch.setattr(self.account, "get_followers", lambda x: result)

        response = self.core.get_followers(self.acc_id)
        assert isinstance(response, list)
        assert response[0].id_, "dummy"

    def test_get_following(self, monkeypatch):
        profile = Profile()
        profile.id_ = "dummy"
        result = [profile]

        monkeypatch.setattr(self.account, "get_following", lambda x: result)

        response = self.core.get_following(self.acc_id)
        assert isinstance(response, list)
        assert response[0].id_, "dummy"

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


    def test_get_user_profile(self, monkeypatch):
        profile = Profile()
        self.account.profile = profile
        result = [profile]

        monkeypatch.setattr(self.account, "get_profile", lambda x: profile)
        monkeypatch.setattr(self.account, "is_friend", lambda x: True)
        monkeypatch.setattr(self.core, "is_muted", lambda x: False)

        profile.id_ = "dummy"
        response = self.core.get_user_profile(self.acc_id)
        assert isinstance(response, Profile)
        assert response.id_, "dummy"

        profile.id_ = "user"
        response = self.core.get_user_profile(self.acc_id, "user")
        assert isinstance(response, Profile)
        assert response.id_, "user"
        assert response.followed_by, True
        assert not response.muted, True

    def test_get_conversation(self, monkeypatch):
        status = Status()
        status.id_ = "321"
        conversation = [status]

        monkeypatch.setattr(self.account, "get_conversation", lambda x: conversation)

        response = self.core.get_conversation(self.acc_id, "123")
        assert isinstance(response, list)
        assert isinstance(response[0], Status)
        assert response[0].id_, "321"

    # Tested by lines
    def test_update_status(self, monkeypatch):
        status = Status()
        monkeypatch.setattr(self.account, "update_status", lambda x, y, z: status)

        response = self.core.update_status(self.acc_id, "Dummy message")
        assert response == status

        response = self.core.update_status(self.acc_id, "Dummy message", "123456")
        assert response == status

        response = self.core.update_status(self.acc_id, "Dummy message", "123456", "/path/to/media")
        assert response == status

    def test_broadcast_status(self, monkeypatch):
        status = Status()
        monkeypatch.setattr(self.account, "update_status", lambda x: status)
        monkeypatch.setattr(self.core, "registered_accounts", lambda: [self.account])

        response = self.core.broadcast_status(None, "Dummy message")
        assert isinstance(response, dict)
        assert isinstance(response["dummy-twitter"], Status)
        assert response["dummy-twitter"] == status

        response = self.core.broadcast_status(["foo-twitter", "bar-twitter"], "Dummy message")
        assert isinstance(response, dict)
        assert isinstance(response["foo-twitter"], Status)
        assert response["foo-twitter"] == status
        assert isinstance(response["bar-twitter"], Status)
        assert response["bar-twitter"] == status

    def test_destroy_status(self, monkeypatch):
        status = Status()
        monkeypatch.setattr(self.account, "destroy_status", lambda x: status)

        response = self.core.destroy_status("dummy-twitter", "123")
        assert isinstance(response, Status)
        assert response == status

    def test_get_single_status(self, monkeypatch):
        status = Status()
        monkeypatch.setattr(self.account, "get_status", lambda x: status)

        response = self.core.get_single_status("dummy-twitter", "123")
        assert isinstance(response, Status)
        assert response == status

    def test_repeat_status(self, monkeypatch):
        status = Status()
        monkeypatch.setattr(self.account, "repeat_status", lambda x: status)

        response = self.core.repeat_status("dummy-twitter", "123")
        assert isinstance(response, Status)
        assert response == status

    def test_mark_status_as_favorite(self, monkeypatch):
        status = Status()
        monkeypatch.setattr(self.account, "mark_as_favorite", lambda x: status)

        response = self.core.mark_status_as_favorite("dummy-twitter", "123")
        assert isinstance(response, Status)
        assert response == status

    def test_unmark_status_as_favorite(self, monkeypatch):
        status = Status()
        monkeypatch.setattr(self.account, "unmark_as_favorite", lambda x: status)

        response = self.core.unmark_status_as_favorite("dummy-twitter", "123")
        assert isinstance(response, Status)
        assert response == status

    def test_send_direct_message(self, monkeypatch):
        status = Status()
        monkeypatch.setattr(self.account, "send_direct_message", lambda x, y: status)

        response = self.core.send_direct_message("dummy-twitter", "foo", "Dummy message")
        assert isinstance(response, Status)
        assert response == status

    def test_destroy_direct_message(self, monkeypatch):
        status = Status()
        monkeypatch.setattr(self.account, "destroy_direct_message", lambda x: status)

        response = self.core.destroy_direct_message("dummy-twitter", "123")
        assert isinstance(response, Status)
        assert response == status

    def test_update_profile(self, monkeypatch):
        profile = Profile()
        monkeypatch.setattr(self.account, "update_profile", lambda w, x, y, z: profile)

        # TODO: Test with no params
        # response = self.core.update_profile(self.acc_id)
        # raise excetion

        response = self.core.update_profile(self.acc_id, fullname="Another fullname")
        assert response == profile
        response = self.core.update_profile(self.acc_id, bio="Dummy bio")
        assert response == profile
        response = self.core.update_profile(self.acc_id, url="http://crazy.url")
        assert response == profile
        response = self.core.update_profile(self.acc_id, location="Nowhere")
        assert response == profile
        response = self.core.update_profile(self.acc_id, "Another fullname", "http://crazy.url",
                "Dummy bio", "Nowhere")
        assert response == profile

    def test_follow(self, monkeypatch):
        profile = Profile()
        profile.username = "foo"
        monkeypatch.setattr(self.account, "follow", lambda x, y: profile)
        monkeypatch.setattr(self.core, "add_friend", lambda x: None)

        response = self.core.follow(self.acc_id, "foo")
        assert response == profile
        response = self.core.follow(self.acc_id, "123", True)
        assert response == profile

    def test_unfollow(self, monkeypatch):
        profile = Profile()
        profile.username = "foo"
        monkeypatch.setattr(self.account, "unfollow", lambda x: profile)
        monkeypatch.setattr(self.core, "remove_friend", lambda x: None)

        response = self.core.unfollow(self.acc_id, "foo")
        assert response == profile

    def test_block(self, monkeypatch):
        profile = Profile()
        profile.username = "foo"
        monkeypatch.setattr(self.account, "block", lambda x: profile)
        monkeypatch.setattr(self.core, "remove_friend", lambda x: None)

        response = self.core.block(self.acc_id, "foo")
        assert response == profile

    def test_unblock(self, monkeypatch):
        profile = Profile()
        profile.username = "foo"
        monkeypatch.setattr(self.account, "unblock", lambda x: profile)

        response = self.core.unblock(self.acc_id, "foo")
        assert response == profile

    def test_report_as_spam(self, monkeypatch):
        profile = Profile()
        profile.username = "foo"
        monkeypatch.setattr(self.account, "report_as_spam", lambda x: profile)
        monkeypatch.setattr(self.core, "remove_friend", lambda x: None)

        response = self.core.report_as_spam(self.acc_id, "foo")
        assert response == profile

    def test_mute(self, monkeypatch):
        monkeypatch.setattr(self.core.config, "append_filter", lambda x: "foo")

        response = self.core.mute("foo")
        assert response == "foo"

    def test_unmute(self, monkeypatch):
        monkeypatch.setattr(self.core.config, "remove_filter", lambda x: "foo")

        response = self.core.unmute("foo")
        assert response == "foo"

    def test_verify_friendship(self, monkeypatch):
        monkeypatch.setattr(self.account, "is_friend", lambda x: True)

        response = self.core.verify_friendship(self.acc_id, "foo")
        assert response is True

        monkeypatch.setattr(self.account, "is_friend", lambda x: False)
        response = self.core.verify_friendship(self.acc_id, "foo")
        assert response is False

    def test_search(self, monkeypatch):
        search = [Status()]

        monkeypatch.setattr(self.account, "search", lambda w, x, y, z: search)

        response = self.core.search(self.acc_id, "dummy", since_id="123", count=200, extra="ble")
        assert isinstance(response, list)
        assert isinstance(response[0], Status)

        response = self.core.search(self.acc_id, "dummy")
        assert isinstance(response, list)
        assert isinstance(response[0], Status)

        response = self.core.search(self.acc_id, "dummy", 200, "123", "ble")
        assert isinstance(response, list)
        assert isinstance(response[0], Status)


    def test_get_profile_image(self, monkeypatch):
        monkeypatch.setattr(self.core, "get_profile_image", lambda x, y, z: "/path/to/ble")

        response = self.core.get_profile_image(self.acc_id, "foo", True)
        assert response == "/path/to/ble"

        response = self.core.get_profile_image(self.acc_id, "foo", False)
        assert response == "/path/to/ble"

        # TODO: Make this work
        #account = Account("twitter", "dummy")
        #account.config = DummyConfig()
        #(handler, path) = tempfile.mkstemp()
        #monkeypatch.setattr(os.path, "join", lambda x, y: path)
        #monkeypatch.setattr(os.path, "isfile", lambda x: True)

        ## Using cache
        #response = self.core.get_profile_image(self.acc_id, "foo")
        #assert response == path

        ## Not using cache
        #monkeypatch.setattr(account, "get_profile_image", lambda x: "/path/to/bla")
        #monkeypatch.setattr(self.core, "fetch_image", lambda x: "123test")
        #response = self.core.get_profile_image(self.acc_id, "foo", False)
        #assert response == path

    def test_get_status_avatar(self, monkeypatch):
        monkeypatch.setattr(self.core, "get_status_avatar", lambda x: "/path/to/ble")

        response = self.core.get_status_avatar("123")
        assert response == "/path/to/ble"

        response = self.core.get_status_avatar("123")
        assert response == "/path/to/ble"

    def test_get_available_trend_locations(self, monkeypatch):
        location = TrendLocation('Global', 1)
        monkeypatch.setattr(self.account, "available_trend_locations", lambda: [location])

        response = self.core.get_available_trend_locations(self.acc_id)
        assert isinstance(response, list)
        assert response[0] == location

    def test_get_trending_topics(self, monkeypatch):
        trend = Trend('Foo')
        monkeypatch.setattr(self.account, "trends", lambda x: [trend])

        response = self.core.get_trending_topics(self.acc_id, "here")
        assert isinstance(response, list)
        assert response[0] == trend

    def test_update_profile_image(self, monkeypatch):
        profile = Profile()
        monkeypatch.setattr(self.account, "update_profile_image", lambda x: profile)

        response = self.core.update_profile_image(self.acc_id, "/path/to/ble")
        assert response == profile

    # Services
    def test_available_short_url_services(self):
        response = self.core.available_short_url_services()
        assert isinstance(response, list)
        assert isinstance(response[0], str)

    def test_short_single_url(self, monkeypatch):
        monkeypatch.setattr(self.core, "get_shorten_url_service", lambda: 'is.gd')
        with pytest.raises(URLAlreadyShort):
            self.core.short_single_url('http://is.gd/blable')

        monkeypatch.setattr(self.core, "short_single_url", lambda x: 'http://is.gd/ble')
        response = self.core.short_single_url('http://my.looooon.url')
        assert response == 'http://is.gd/ble'

    def test_short_url_in_message(self, monkeypatch):
        monkeypatch.setattr(self.core, "get_shorten_url_service", lambda: 'is.gd')

        message = "Hello, this is a message with a dumb url http://dumb.url.com"
        message_with_short_url = "Hello, this is a message with a short url http://is.gd/dumb"
        message_with_no_url = "Hello, this is a message with no url"
        message_expected = "Hello, this is a message with a dumb url http://is.gd/dumb"

        with pytest.raises(NoURLToShorten):
            self.core.short_url_in_message(message_with_no_url)

        monkeypatch.setattr(self.core, "short_single_url", lambda x: 'http://is.gd/dumb')
        response = self.core.short_url_in_message(message)
        assert response == message_expected

    def test_available_preview_media_services(self):
        response = self.core.available_preview_media_services()
        assert isinstance(response, list)
        assert isinstance(response[0], str)

    def test_preview_media(self, monkeypatch):
        media = Media.new_image('foo', 'binary content')
        with pytest.raises(PreviewServiceNotSupported):
            self.core.preview_media('http://unsupported.service.com/ble')

        monkeypatch.setattr(self.core, "preview_media", lambda x: media)
        response = self.core.preview_media('http://pic.twitter.com/ble')
        assert isinstance(response, Media)

    def test_available_upload_media_services(self):
        response = self.core.available_upload_media_services()
        assert isinstance(response, list)
        assert isinstance(response[0], str)

    def test_upload_media(self, monkeypatch):
        monkeypatch.setattr(self.core, "upload_media", lambda x, y, z: 'http://ima.ge/bla')

        response = self.core.upload_media(self.acc_id, '/path/to/file', "Dummy message")
        assert response == 'http://ima.ge/bla'

    # Configuration
    def test_get_shorten_url_service(self):
        response = self.core.get_shorten_url_service()
        assert isinstance(response, str)

    def test_get_upload_media_service(self):
        response = self.core.get_upload_media_service()
        assert isinstance(response, str)

    def test_set_shorten_url_service(self, monkeypatch):
        monkeypatch.setattr(self.core.config, "write", lambda x, y, z: None)

        response = self.core.set_shorten_url_service('foo')
        assert response is None

    def test_set_upload_media_service(self, monkeypatch):
        monkeypatch.setattr(self.core.config, "write", lambda x, y, z: None)

        response = self.core.set_upload_media_service('foo')
        assert response is None

    def test_is_muted(self, monkeypatch):
        monkeypatch.setattr(self.core.config, "load_filters", lambda: ['@foo', '@bar'])

        response = self.core.is_muted('foo')
        assert response == True
        response = self.core.is_muted('baz')
        assert response == False

    def test_get_default_browser(self, monkeypatch):
        monkeypatch.setattr(self.core.config, "read", lambda x, y: None)
        response = self.core.get_default_browser()
        assert response is None

        monkeypatch.setattr(self.core.config, "read", lambda x, y: 'chromium')
        response = self.core.get_default_browser()
        assert response == 'chromium'
