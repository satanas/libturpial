import pytest
import requests

from libturpial.lib.services.media.preview.base import PreviewMediaService

from tests.helpers import DummyResponse

class TestPreviewBase:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        self.preview = PreviewMediaService()

    def test_do_service(self):
        with pytest.raises(NotImplementedError):
            self.preview.do_service('http://example.org')

    def test_get_content_from_url(self, monkeypatch):
        monkeypatch.setattr(requests, 'get', lambda x: DummyResponse('loremipsum'))

        response = self.preview._get_content_from_url('http://example.com')
        assert response == 'loremipsum'

    def test_get_id_from_url(self):
        response = self.preview._get_id_from_url('http://example.org/1')
        assert response == '1'
