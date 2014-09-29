from libturpial.api.models.column import Column

class TestColumn:
    @classmethod
    def setup_class(self):
        self.column = Column("foo-twitter", "timeline")

    def test_structure(self):
        assert self.column.size == 0
        assert self.column.id_ == "foo-twitter-timeline"
        assert self.column.slug == "timeline"
        assert self.column.updating == False
        assert self.column.singular_unit == "tweet"
        assert self.column.plural_unit == "tweets"

    def test_repr(self):
        assert repr(self.column) == "libturpial.api.models.Column foo-twitter-timeline"
