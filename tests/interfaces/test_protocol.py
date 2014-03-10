import pytest

from libturpial.exceptions import NotSupported
from libturpial.api.models.entity import Entity
from libturpial.lib.interfaces.protocol import Protocol

class TestProtocol:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        pass

    def test_convert_time(self, monkeypatch):
        monkeypatch.setattr('libturpial.lib.interfaces.protocol.Protocol.initialize_http', lambda x: None)
        protocol = Protocol()
        protocol.hashtags_url = 'http://hashtags.url.com'

        response = protocol.convert_time("Tue Mar 13 00:12:41 +0000 2007")
        assert response.tm_year == 2007
        assert response.tm_mon == 3
        assert response.tm_mday == 13
        assert response.tm_hour == 0
        assert response.tm_min == 12
        assert response.tm_sec == 41

        response = protocol.convert_time("Wed, 08 Apr 2009 19:22:10 +0000")
        assert response.tm_year == 2009
        assert response.tm_mon == 4
        assert response.tm_mday == 8
        assert response.tm_hour == 19
        assert response.tm_min == 22
        assert response.tm_sec == 10

    def test_get_str_time(self, monkeypatch):
        monkeypatch.setattr('libturpial.lib.interfaces.protocol.Protocol.initialize_http', lambda x: None)
        protocol = Protocol()
        protocol.hashtags_url = 'http://hashtags.url.com'

        response = protocol.get_str_time("Tue Mar 13 00:12:41 +0000 2007")
        assert response == "Mar 13, 12:12 AM"

    def test_get_int_time(self, monkeypatch):
        monkeypatch.setattr('libturpial.lib.interfaces.protocol.Protocol.initialize_http', lambda x: None)
        protocol = Protocol()
        protocol.hashtags_url = 'http://hashtags.url.com'

        response = int(protocol.get_int_time("Tue Mar 13 00:12:41 +0000 2007"))
        assert response == 1173759161

    def test_get_entities(self, monkeypatch):
        monkeypatch.setattr('libturpial.lib.interfaces.protocol.Protocol.initialize_http', lambda x: None)
        protocol = Protocol()
        protocol.hashtags_url = 'http://hashtags.url.com'

        status = {
                'text': '@lorem ipsum @foobar, #somehashtag, a !group, more #hashtags and even a valid URL http://example.com.'
        }
        entities = protocol.get_entities(status)
        assert len(entities['urls']) == 1
        assert isinstance(entities['urls'][0], Entity)
        assert entities['urls'][0].url == 'http://example.com'
        assert len(entities['hashtags']) == 2
        assert isinstance(entities['hashtags'][0], Entity)
        assert '#somehashtag' in entities['hashtags'][0].display_text
        assert '#hashtags' in entities['hashtags'][1].display_text
        assert len(entities['mentions']) == 2
        assert isinstance(entities['mentions'][0], Entity)
        assert entities['mentions'][0].display_text == '@lorem'
        assert entities['mentions'][1].display_text == '@foobar'
        assert len(entities['groups']) == 0

    def test_not_implemented_methods(self, monkeypatch):
        with pytest.raises(NotImplementedError):
            protocol = Protocol()

        monkeypatch.setattr('libturpial.lib.interfaces.protocol.Protocol.initialize_http', lambda x: None)
        protocol = Protocol()
        protocol.hashtags_url = 'http://hashtags.url.com'

        with pytest.raises(NotSupported):
            protocol.request_access()

        with pytest.raises(NotImplementedError):
            protocol.setup_user_credentials()

        with pytest.raises(NotImplementedError):
            protocol.json_to_profile(None)

        with pytest.raises(NotImplementedError):
            protocol.json_to_status(None)

        with pytest.raises(NotImplementedError):
            protocol.json_to_ratelimit(None)

        with pytest.raises(NotImplementedError):
            protocol.json_to_list(None)

        with pytest.raises(NotImplementedError):
            protocol.verify_credentials()

        with pytest.raises(NotImplementedError):
            protocol.verify_credentials_provider()

        with pytest.raises(NotImplementedError):
            protocol.get_timeline(1, '123')

        with pytest.raises(NotImplementedError):
            protocol.get_replies(1, '123')

        with pytest.raises(NotImplementedError):
            protocol.get_directs(1, '123')

        with pytest.raises(NotImplementedError):
            protocol.get_directs_sent(1, '123')

        with pytest.raises(NotImplementedError):
            protocol.get_sent(1, '123')

        with pytest.raises(NotImplementedError):
            protocol.get_favorites(1)

        with pytest.raises(NotImplementedError):
            protocol.get_public_timeline(1, '123')

        with pytest.raises(NotImplementedError):
            protocol.get_lists('foo')

        with pytest.raises(NotImplementedError):
            protocol.get_list_statuses(1, '123')

        with pytest.raises(NotImplementedError):
            protocol.get_conversation(1)

        with pytest.raises(NotImplementedError):
            protocol.get_status(1)

        with pytest.raises(NotImplementedError):
            protocol.get_followers(False)

        with pytest.raises(NotImplementedError):
            protocol.get_following(False)

        with pytest.raises(NotImplementedError):
            protocol.get_profile('foo')

        with pytest.raises(NotImplementedError):
            protocol.get_blocked()

        with pytest.raises(NotImplementedError):
            protocol.get_rate_limits()

        with pytest.raises(NotImplementedError):
            protocol.get_repeaters('123', True)

        with pytest.raises(NotImplementedError):
            protocol.update_profile('Foo', '', '', '')

        with pytest.raises(NotImplementedError):
            protocol.update_status('text', '123', '/path/to/ble')

        with pytest.raises(NotImplementedError):
            protocol.destroy_status('123')

        with pytest.raises(NotImplementedError):
            protocol.repeat_status('123')

        with pytest.raises(NotImplementedError):
            protocol.mark_as_favorite('123')

        with pytest.raises(NotImplementedError):
            protocol.unmark_as_favorite('123')

        with pytest.raises(NotImplementedError):
            protocol.follow('foo', False)

        with pytest.raises(NotImplementedError):
            protocol.unfollow('foo')

        with pytest.raises(NotImplementedError):
            protocol.send_direct_message('foo', 'text')

        with pytest.raises(NotImplementedError):
            protocol.destroy_direct_message('123')

        with pytest.raises(NotImplementedError):
            protocol.block('foo')

        with pytest.raises(NotImplementedError):
            protocol.unblock('foo')

        with pytest.raises(NotImplementedError):
            protocol.report_as_spam('foo')

        with pytest.raises(NotImplementedError):
            protocol.search('#foo', 1, '123', 'ble')

        with pytest.raises(NotImplementedError):
            protocol.is_friend('foo')

        with pytest.raises(NotImplementedError):
            protocol.get_profile_image('foo')

        with pytest.raises(NotImplementedError):
            protocol.trends('1')

        with pytest.raises(NotImplementedError):
            protocol.available_trend_locations()

        with pytest.raises(NotImplementedError):
            protocol.update_profile_image('/path/to/ble')
