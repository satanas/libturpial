import os
import pytest
import __builtin__

from libturpial.config import *

from tests.helpers import DummyFileHandler


class DummyConfigParser:
    def read(self, value):
        pass
    def sections(self):
        return []
    def options(self):
        return []
    def add_section(self, value):
        pass
    def set(self, x, y, z):
        pass
    def write(self, value):
        pass
    def has_section(self, value):
        return True

class DummyGenerator:
    def __init__(self, array):
        self.array = array
    def __iter__(self):
        return iter(self.array)

class TestConfigBase:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        self.default = {
            'foo': {
                'bar': 987,
            },
            'bla': {
                'ble': 'on',
                'bli': 'off',
            }
        }

        self.config_base = ConfigBase(self.default)

        monkeypatch.setattr(__builtin__, 'open', lambda x, y: DummyFileHandler())
        monkeypatch.setattr(self.config_base.cfg, 'add_section', lambda x: None)
        monkeypatch.setattr(self.config_base.cfg, 'set', lambda x, y, z: None)
        monkeypatch.setattr(self.config_base.cfg, 'write', lambda x: None)

        self.config_base.configpath = '/tmp/foo'

    def test_default_values(self):
        assert 'General' in APP_CFG
        assert 'update-interval' in APP_CFG['General']
        assert 'queue-interval' in APP_CFG['General']
        assert 'minimize-on-close' in APP_CFG['General']
        assert 'statuses' in APP_CFG['General']
        assert 'Columns' in APP_CFG
        assert 'Services' in APP_CFG
        assert 'shorten-url' in APP_CFG['Services']
        assert 'upload-pic' in APP_CFG['Services']
        assert 'Proxy' in APP_CFG
        assert 'username' in APP_CFG['Proxy']
        assert 'password' in APP_CFG['Proxy']
        assert 'server' in APP_CFG['Proxy']
        assert 'port' in APP_CFG['Proxy']
        assert 'protocol' in APP_CFG['Proxy']
        assert 'Advanced' in APP_CFG
        assert 'socket-timeout' in APP_CFG['Advanced']
        assert 'show-user-avatars' in APP_CFG['Advanced']
        assert 'Window' in APP_CFG
        assert 'size' in APP_CFG['Window']
        assert 'Notifications' in APP_CFG
        assert 'on-updates' in APP_CFG['Notifications']
        assert 'on-actions' in APP_CFG['Notifications']
        assert 'Sounds' in APP_CFG
        assert 'on-login' in APP_CFG['Sounds']
        assert 'on-updates' in APP_CFG['Sounds']
        assert 'Browser' in APP_CFG
        assert 'cmd' in APP_CFG['Browser']

        assert 'OAuth' in ACCOUNT_CFG
        assert 'key' in ACCOUNT_CFG['OAuth']
        assert 'secret' in ACCOUNT_CFG['OAuth']
        assert 'Login' in ACCOUNT_CFG
        assert 'username' in ACCOUNT_CFG['Login']
        assert 'protocol' in ACCOUNT_CFG['Login']

    def test_init_config_base(self):
        config_base = ConfigBase(self.default)
        assert config_base.filepath == ''
        assert config_base.extra_sections == {}
        assert 'foo' in config_base.default

        config_base = ConfigBase(None)
        assert 'Advanced' in config_base.default

    def test_register_extra_option(self, monkeypatch):
        monkeypatch.setattr(self.config_base, 'write', lambda x, y, z: None)
        self.config_base.register_extra_option('foo', 'baz', 000)
        assert 'baz' in self.config_base.extra_sections['foo']
        assert self.config_base.extra_sections['foo']['baz'] == 000

    def test_create(self, monkeypatch):
        self.config_base.create()
        assert self.config_base._ConfigBase__config['foo']['bar'] == 987

    def test_load_failsafe(self):
        config_base = ConfigBase(self.default)
        config_base.load_failsafe()
        assert config_base._ConfigBase__config == self.default

    def test_save(self, monkeypatch):
        self.config_base.save({'foo2': {'bar2': 2}})
        assert self.config_base._ConfigBase__config['foo2']['bar2'] == 2

    def test_write(self, monkeypatch):
        monkeypatch.setattr(self.config_base.cfg, 'has_section', lambda x: False)
        self.config_base.write('foo', 'qux', -1)
        assert self.config_base._ConfigBase__config['foo']['qux'] == -1

        monkeypatch.setattr(self.config_base.cfg, 'has_section', lambda x: True)
        self.config_base.write('foo', 'qux', 99)
        assert self.config_base._ConfigBase__config['foo']['qux'] == 99

    def test_write_section(self, monkeypatch):
        monkeypatch.setattr(self.config_base.cfg, 'remove_section', lambda x: False)
        monkeypatch.setattr(self.config_base.cfg, 'has_section', lambda x: False)

        self.config_base.write_section('foo', {'ble': 2})
        assert len(self.config_base._ConfigBase__config['foo']) == 1
        assert self.config_base._ConfigBase__config['foo']['ble'] == 2

    def test_read(self):
        self.config_base.create()
        value = self.config_base.read('foo', 'bar')
        assert value == 987
        value = self.config_base.read('bla', 'ble', True)
        assert value
        value = self.config_base.read('bla', 'bli', False)
        assert value == 'off'
        value = self.config_base.read('dummy', 'var')
        assert value is None

    def test_read_section(self):
        self.config_base.create()
        section = self.config_base.read_section('foo')
        assert section == self.default['foo']

        section = self.config_base.read_section('faa')
        assert section is None

    def test_read_all(self):
        self.config_base.create()
        all_ = self.config_base.read_all()
        assert all_ == self.default


class TestAppConfig:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self, monkeypatch):
        self.default = {
            'foo': {
                'bar': 987,
            },
            'bla': {
                'ble': 'on',
                'bli': 'off',
            }
        }

        monkeypatch.setattr(os, 'makedirs', lambda x: None)
        monkeypatch.setattr(__builtin__, 'open', lambda x, y: DummyFileHandler())
        monkeypatch.setattr(ConfigParser, 'ConfigParser', lambda: DummyConfigParser())

        self.app_config = AppConfig('/tmp/user', self.default)

    def test_init(self):
        assert self.app_config.configpath == '/tmp/user/config'
        assert self.app_config.filterpath == '/tmp/user/filtered'
        assert self.app_config.friendspath == '/tmp/user/friends'

    def test_load_filters(self, monkeypatch):
        monkeypatch.setattr(__builtin__, 'open', lambda x, y: DummyFileHandler(['@foo', 'bar', "\n"]))
        filters = self.app_config.load_filters()
        assert filters[0] == '@foo'
        assert len(filters) == 2

    # TODO: How to test that this works? Return 0 maybe?
    def test_save_filters(self):
        assert self.app_config.save_filters(['foo', 'bar']) == None

    # TODO: How to test that this works? Return 0 maybe?
    def test_append_filter(self, monkeypatch):
        assert self.app_config.append_filter('@dummy') == None
        monkeypatch.setattr(self.app_config, 'load_filters', lambda: ['@dummy'])
        with pytest.raises(ExpressionAlreadyFiltered):
            self.app_config.append_filter('@dummy')

    # TODO: How to test that this works? Return 0 maybe?
    def test_remove_filter(self, monkeypatch):
        monkeypatch.setattr(self.app_config, 'load_filters', lambda: ['@foo', 'bar', '@dummy'])
        monkeypatch.setattr(self.app_config, 'save_filters', lambda x: None)
        assert self.app_config.remove_filter('bar') == None

    def test_load_friends(self, monkeypatch):
        monkeypatch.setattr(__builtin__, 'open', lambda x, y: DummyFileHandler(['foo', 'bar\n', "\n"]))
        friends = self.app_config.load_friends()
        assert friends == ['foo', 'bar']

    # TODO: How to test that this works? Return 0 maybe?
    def test_save_friends(self):
        assert self.app_config.save_friends(['foo', 'bar']) == None

    def test_get_stored_accounts(self, monkeypatch):
        monkeypatch.setattr(os, 'walk', lambda x: DummyGenerator([('foopath', ['dirpath1', 'dirpath2'], ['filename1'])]))
        monkeypatch.setattr(os.path, 'isfile', lambda x: True)
        accounts = self.app_config.get_stored_accounts()
        assert accounts == ['dirpath1', 'dirpath2']

    def test_get_stored_columns(self, monkeypatch):
        temp = {'column3': 'foo-twitter-timeline', 'column1': 'foo-twitter-directs', 'column2': 'foo-twitter-sent'}
        monkeypatch.setattr(self.app_config, 'read_section', lambda x: temp)
        columns = self.app_config.get_stored_columns()
        assert columns[0] == 'foo-twitter-directs'
        assert columns[1] == 'foo-twitter-sent'
        assert columns[2] == 'foo-twitter-timeline'

        temp = {'column1': '', 'column2': ''}
        monkeypatch.setattr(self.app_config, 'read_section', lambda x: temp)
        columns = self.app_config.get_stored_columns()
        assert len(columns) == 0

    def test_get_proxy(self, monkeypatch):
        proxy_temp = {'server': '127.0.0.1', 'port': 80, 'protocol': 'http', 'username': '', 'password': ''}
        monkeypatch.setattr(self.app_config, 'read_section', lambda x: proxy_temp)
        proxy = self.app_config.get_proxy()
        assert proxy.secure == False
        assert proxy.host == '127.0.0.1'
        assert proxy.port == 80
        assert proxy.username == ''
        assert proxy.password == ''
        proxy_temp['protocol'] = 'https'
        proxy = self.app_config.get_proxy()
        assert proxy.secure == True

    def test_get_socket_timeout(self, monkeypatch):
        monkeypatch.setattr(self.app_config, 'read', lambda x, y: 9999)
        assert self.app_config.get_socket_timeout() == 9999

    # TODO: How to test that this works? Return 0 maybe?
    def test_delete(self, monkeypatch):
        monkeypatch.setattr(os, 'remove', lambda x: None)
        assert self.app_config.delete() == None


