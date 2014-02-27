import pytest

from libturpial.exceptions import *

class TestExceptions:
    def test_loading_account_exception(self):
        exc = ErrorLoadingAccount("Dummy message")
        temp = "%s" % exc
        assert exc.message == "Dummy message"
        assert temp == "'Dummy message'"

    def test_dirrect_message_exception(self):
        exc = ErrorSendingDirectMessage("Dummy message")
        temp = "%s" % exc
        assert exc.message == "Dummy message"
        assert temp == "'Dummy message'"

    def test_url_shorten_exception(self):
        exc = URLShortenError("Dummy message")
        assert exc.message == "Dummy message"

    def test_upload_image_exception(self):
        exc = UploadImageError("Dummy message")
        assert exc.message == "Dummy message"
        exc = UploadImageError()
        assert exc.message == None
