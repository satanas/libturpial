from libturpial.api.models.status import Status
from libturpial.api.models.entity import Entity
from libturpial.api.models.client import Client

class TestStatus:
    @classmethod
    def setup_class(self):
        self.status = Status()
        self.status.account_id = "dummy-twitter"
        self.status.username = "dummy"

    def test_structure(self):
        self.status.id_ = "123"
        self.status.original_status_id = "123"
        self.status.created_at = ""
        self.status.avatar = "my_avatar.png"
        self.status.text = "Tweet text"
        self.status.in_reply_to_id = "123"
        self.status.in_reply_to_user = "bar"
        self.status.is_favorite = False
        self.status.is_protected = False
        self.status.is_verified = True
        self.status.repeated_by = "baz"
        self.status.datetime = "01-01-1900 00:00"
        self.status.timestamp = 123456789
        self.status.entities =  {
            'urls': [],
            'hashtags': [],
            'mentions': [],
            'groups': [],
        }
        self.status.type_ = Status.NORMAL
        self.status.is_own = True
        self.status.repeated = False
        self.status.repeated_count = None
        self.status.local_timestamp = 123456789
        self.status.source = None

    def test_is_direct(self):
        assert self.status.is_direct() == False
        self.status.type_ = Status.DIRECT
        assert self.status.is_direct() == True

    def test_get_mentions(self):
        entities = {
            'mentions': [
                Entity(self.status.account_id, "@dummy", "@dummy", "@dummy"),
                Entity(self.status.account_id, "@foo", "@foo", "@foo"),
                Entity(self.status.account_id, "@bar", "@bar", "@bar"),
                Entity(self.status.account_id, "@baz", "@baz", "@baz"),
            ],
        }
        self.status.entities = entities

        mentions = self.status.get_mentions()
        assert isinstance(mentions, list)
        assert len(mentions) == 4
        assert mentions[0] == "dummy"
        assert mentions[1] == "foo"
        assert mentions[2] == "bar"
        assert mentions[3] == "baz"

        self.status.entities = {}
        mentions = self.status.get_mentions()
        assert isinstance(mentions, list)
        assert len(mentions) == 1
        assert mentions[0] == "dummy"

    def test_get_protocol_id(self):
        response = self.status.get_protocol_id()
        assert response == "twitter"

    def test_get_source(self):
        self.status.get_source(None)
        assert self.status.source is None

        self.status.get_source('web')
        assert isinstance(self.status.source, Client)
        assert self.status.source.name == "web"
        assert self.status.source.url == "http://twitter.com"

        self.status.get_source('<a href="http://fooclient.com">Foo client</a>')
        assert isinstance(self.status.source, Client)
        assert self.status.source.name == "Foo client"
        assert self.status.source.url == "http://fooclient.com"

        self.status.get_source('Bar client')
        assert isinstance(self.status.source, Client)
        assert self.status.source.name == "Bar client"
        assert self.status.source.url is None

    def test_equality(self):
        status = Status()
        status.id_ = "456"
        assert not status == self.status

        status.id_ = "123"
        assert status == self.status

