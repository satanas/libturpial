import pytest
import urllib.request, urllib.error, urllib.parse

try:
    import json
except ImportError:
    import simplejson as json

from libturpial.lib.interfaces.service import GenericService

class DummyHandler:
    def read(self):
        return "123"

class TestService:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        self.service = GenericService()

    def test_get_request(self, monkeypatch):
        monkeypatch.setattr(urllib.request, 'urlopen', lambda x, y: DummyHandler())
        response = self.service._get_request('http://example.com')
        assert response == '123'
        response = self.service._get_request('http://example.com', 'dummy_data')
        assert response == '123'

    def test_json_request(self, monkeypatch):
        monkeypatch.setattr(urllib.request, 'urlopen', lambda x: DummyHandler())
        monkeypatch.setattr(json, 'loads', lambda x: {'response': '123'})
        response = self.service._json_request('http://example.com')
        assert response == {'response': '123'}

    def test_quote_url(self):
        quoted_url = self.service._quote_url('http://example.com')
        assert quoted_url == 'http%3A%2F%2Fexample.com'

    def test_parse_xml(self):
        xml_text = "<root><test><play>Dummy message</play></test></root>"
        parsed_text = self.service._parse_xml('play', xml_text)
        assert parsed_text == "Dummy message"

    def test_do_service(self):
        with pytest.raises(NotImplementedError):
            self.service.do_service('bla')
