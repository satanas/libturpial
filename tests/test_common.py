import pytest

from libturpial.common import *

class TestCommon:
    @classmethod
    def setup_class(self):
        self.account_id = "dummy-twitter"

    def test_get_username(self):
        username = get_username_from(self.account_id)
        assert username == "dummy"

    def test_get_protocol(self):
        protocol = get_protocol_from(self.account_id)
        assert protocol == "twitter"

    def test_get_account_id(self):
        account_id = get_account_id_from("foo-twitter-timeline")
        assert account_id == "foo-twitter"

    def test_get_column_slug(self):
        column_id = "dummy-twitter-timeline"
        slug = get_column_slug_from(column_id)
        assert slug == "timeline"

    def test_get_preview_service(self):
        preview = get_preview_service_from_url("http://pic.twitter.com/ble")
        assert preview != None

        preview = get_preview_service_from_url("http://unknown.service.com/bla")
        assert preview == None

    def test_is_preview_service_supported(self):
        preview = is_preview_service_supported("http://pic.twitter.com/ble")
        assert preview

        preview = is_preview_service_supported("http://unknown.service.com/bla")
        assert not preview

