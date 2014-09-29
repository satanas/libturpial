from libturpial.api.models.list import List

class TestColumn:
    @classmethod
    def setup_class(self):
        self.list_ = List()
        self.list_.id_ = "foo-twitter-list"
        self.list_.slug = "list"
        self.list_.title = "My List"
        self.list_.suscribers = []
        self.list_.description = "Foo list"
        self.list_.single_unit = "tweet"
        self.list_.plural_unit = "tweets"

    def test_structure(self):
        assert self.list_.id_ == "foo-twitter-list"
        assert self.list_.slug == "list"
        assert self.list_.title == "My List"
        assert self.list_.suscribers == []
        assert self.list_.description == "Foo list"
        assert self.list_.single_unit == "tweet"
        assert self.list_.plural_unit == "tweets"

    def test_repr(self):
        assert repr(self.list_) == "libturpial.api.models.List foo-twitter-list"
