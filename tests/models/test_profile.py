import pytest

from libturpial.api.models.profile import Profile

class TestProfile:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        self.profile = Profile()
        self.profile.username = 'foo'
        self.profile.account_id = 'foo-twitter'
        self.profile.fullname = "Foo Bar"

    def test_structure(self):
        profile = Profile()
        assert profile.id_ == None
        assert profile.account_id == None
        assert profile.fullname == None
        assert profile.username == None
        assert profile.avatar == None
        assert profile.location == ''
        assert profile.url == ''
        assert profile.bio == ''
        assert profile.following == None
        assert profile.followed_by == None
        assert profile.follow_request == False
        assert profile.followers_count == 0
        assert profile.friends_count == 0
        assert profile.link_color == None
        assert profile.statuses_count == 0
        assert profile.favorites_count == 0
        assert profile.last_update == None
        assert profile.last_update_id == None
        assert profile.recent_updates == []
        assert profile.tmp_avatar_path == None
        assert profile.protected == False
        assert profile.verified == False
        assert profile.muted == False

    def test_repr(self):
        assert str(self.profile) == "libturpial.api.models.Profile foo"

    def test_is_me(self, monkeypatch):
        assert self.profile.is_me() == True
        monkeypatch.setattr(self.profile, 'username', 'dummy')

        assert self.profile.is_me() == False

    def test_get_protocol_id(self, monkeypatch):
        assert self.profile.get_protocol_id() == 'twitter'

        monkeypatch.setattr(self.profile, 'account_id', None)
        assert self.profile.get_protocol_id() == None
