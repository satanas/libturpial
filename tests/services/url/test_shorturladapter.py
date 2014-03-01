import pytest

from libturpial.lib.services.url import ShortUrlAdapter

class DummyShrinker:
    def shrink(self, arg):
        return "foo"

def test_do_service():
    short = ShortUrlAdapter(DummyShrinker())
    assert short.do_service('http://my.really.looooong.url.com') == 'foo'

