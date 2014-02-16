import pytest

from libturpial.exceptions import *
from libturpial.config import AppConfig
from libturpial.api.models.column import Column
from libturpial.api.managers.columnmanager import ColumnManager


class TestColumnManager:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        config = AppConfig()
        columns = ["foo-twitter-timeline", "bar-twitter-replies"]
        monkeypatch.setattr(config, "get_stored_columns", lambda: columns)

        self.colman = ColumnManager(config)

    def test_init(self):
        assert len(self.colman) == 2

    # TODO: Test iterator
    def test_iteration(self):
        pass

    # TODO: Test private methods
    def test_count(self):
        pass

    def test_register(self, monkeypatch):
        with pytest.raises(ColumnAlreadyRegistered):
            self.colman.register("foo-twitter-timeline")

        monkeypatch.setattr(self.colman.config, "write", lambda x, y, z: None)
        response = self.colman.register("ble-twitter-timeline")
        assert response == "ble-twitter-timeline"

    def test_unregister(self, monkeypatch):
        monkeypatch.setattr(self.colman.config, "write_section", lambda x, y: None)

        response = self.colman.unregister("foo-twitter-timeline")
        assert response == "foo-twitter-timeline"

    def test_get(self):
        response = self.colman.get("foo-twitter-timeline")
        assert isinstance(response, Column)

        response = self.colman.get("bar-twitter-timeline")
        assert response is None

    def test_columns(self):
        response = self.colman.columns()
        assert isinstance(response, dict)
        assert len(response) == 2

    def test_columns_by_order(self, monkeypatch):
        monkeypatch.setattr(self.colman.config, "read", lambda x, y: None)
        response = self.colman.columns_by_order()
        assert isinstance(response, list)
        assert len(response) == 0

    def test_is_registered(self):
        response = self.colman.is_registered("foo-twitter-timeline")
        assert response == True

        response = self.colman.is_registered("bar-twitter-timeline")
        assert response == False
