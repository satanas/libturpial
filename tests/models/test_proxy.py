from libturpial.api.models.proxy import Proxy

class TestProxy:
    @classmethod
    def setup_class(self):
        self.proxy = Proxy("foo-twitter", "timeline")

    def test_init(self):
        proxy = Proxy("127.0.0.1", "80")
        assert proxy.host == "127.0.0.1"
        assert proxy.port == "80"
        assert proxy.secure == False
        assert proxy.username == None
        assert proxy.password == None

        proxy = Proxy("127.0.0.2", "8080", username='foo', password='123', secure=True)
        assert proxy.host == "127.0.0.2"
        assert proxy.port == "8080"
        assert proxy.secure == True
        assert proxy.username == 'foo'
        assert proxy.password == '123'

    def test_to_url_config(self):
        proxy = Proxy("", "")
        assert proxy.to_url_config() == {}

        proxy = Proxy('127.0.0.1', '80', secure=True)
        assert proxy.to_url_config() == {'https': 'https://127.0.0.1:80'}

        proxy = Proxy('127.0.0.1', '80', username='foo', password='bar')
        assert proxy.to_url_config() == {'http': 'http://foo:bar@127.0.0.1:80'}
