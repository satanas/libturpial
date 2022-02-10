import pytest
import builtins

from libturpial.api.models.media import Media

from tests.helpers import DummyFileHandler

class TestMedia:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        monkeypatch.setattr(builtins, 'open', lambda x, y: DummyFileHandler())

    def test_init(self, monkeypatch):
        media = Media(Media.IMAGE, 'foo', 'binary', path='/path/to/ble/', info='lorem ipsum')
        assert media.path == '/path/to/ble/'
        assert media.content == 'binary'

        media = Media(Media.IMAGE, 'foo', 'binary')
        assert media.path != None
        assert media.info == None
        assert media.content == 'binary'

    def test_new_image(self, monkeypatch):
        media = Media.new_image('foo', 'binary', path='/path/to/ble', info='lorem ipsum')
        assert isinstance(media, Media)

    def test_save_content(self, monkeypatch):
        media = Media(Media.IMAGE, 'foo', 'binary', path='/path/to/ble/', info='lorem ipsum')
        # TODO: How test that this works?
        assert media.save_content() == None

        def raise_ex():
            raise KeyError
        monkeypatch.setattr(builtins, 'open', lambda x, y: raise_ex())

        media = Media(Media.IMAGE, 'foo', 'binary', path='/path/to/ble/', info='lorem ipsum')
        assert media.save_content() == None

    def test_type(self):
        media = Media(Media.VIDEO, 'foo', 'binary', path='/path/to/ble/', info='lorem ipsum')
        assert media.is_video()

        media = Media(Media.IMAGE, 'foo', 'binary', path='/path/to/ble/', info='lorem ipsum')
        assert media.is_image()

        media = Media(Media.MAP, 'foo', 'binary', path='/path/to/ble/', info='lorem ipsum')
        assert media.is_map()



