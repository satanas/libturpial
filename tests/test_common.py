import os
import sys
import pytest
import logging

from libturpial.common import *
from libturpial.common.tools import *

class TestCommon:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
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

    def test_clean_bytecodes(self, monkeypatch):
        path = os.path.join('..', __file__)
        monkeypatch.setattr(os, 'remove', lambda x: None)

        clean_bytecodes(path, logging)

    def test_detect_os(self, monkeypatch):
        monkeypatch.setattr(sys, 'platform', 'linux')
        assert detect_os() == OS_LINUX

        monkeypatch.setattr(sys, 'platform', 'win32')
        assert detect_os() == OS_WINDOWS

        monkeypatch.setattr(sys, 'platform', 'darwin')
        assert detect_os() == OS_MAC

        monkeypatch.setattr(sys, 'platform', 'java')
        assert detect_os() == OS_JAVA

        monkeypatch.setattr(sys, 'platform', 'foobar')
        assert detect_os() == OS_UNKNOWN

    def test_get_urls(self):
        text = "Dumb test http://google.com with more than (www.foobar.com) one URL http://www.anotherexample.org."
        urls = get_urls(text)
        assert "http://google.com" in urls
        assert "www.foobar.com" in urls
        assert "http://www.anotherexample.org" in urls

    def test_timestamp_to_localtime(self, monkeypatch):
        class DummyTime:
            def __init__(self, value=0):
                self.tm_isdst = value

        monkeypatch.setattr(time, 'timezone', 89)
        monkeypatch.setattr(time, 'localtime', lambda: DummyTime(0))
        localtime = timestamp_to_localtime(123456789)
        assert localtime == 123456700

        monkeypatch.setattr(time, 'altzone', 6000)
        monkeypatch.setattr(time, 'localtime', lambda: DummyTime(1))
        localtime = timestamp_to_localtime(123456789)
        assert localtime == 123450789

