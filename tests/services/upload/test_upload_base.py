import pytest
import requests

from libturpial.lib.services.media.upload.base import UploadService

from tests.helpers import DummyAccount, DummyProtocol, DummyResponse

class TestUploadService:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        pass

    def test_upload_pic(self, monkeypatch):
        account = DummyAccount()
        account.protocol = DummyProtocol()

        temp = DummyResponse('ble')
        fields = {'media': 'ble'}
        files = {'path': '/tmp/dummy'}
        custom_headers = {'Agent': 'DummyAgent'}
        monkeypatch.setattr(requests, 'post', lambda w, files, data, headers: temp)

        upload_service = UploadService('example.com', 'example.com/v1')
        response = upload_service._upload_pic(account, fields, files, custom_headers)
        assert response == 'ble'
