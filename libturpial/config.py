# -*- coding: utf-8 -*-

"""Module to handle basic configuration of Turpial"""

import os
import base64
import shutil
import logging
import ConfigParser

from libturpial.common import get_username_from, get_protocol_from
from libturpial.exceptions import EmptyOAuthCredentials, EmptyBasicCredentials, \
        ExpressionAlreadyFiltered

try:
    from xdg import BaseDirectory
    XDG_CACHE = True
except:
    XDG_CACHE = False

APP_CFG = {
    'General':{
        'update-interval': '5',
        'queue-interval': '30',
        'statuses': '60',
    },
    'Columns':{
    },
    'Services':{
        'shorten-url': 'is.gd',
        'upload-pic': 'twitpic',
    },
    'Proxy':{
        'username': '',
        'password': '',
        'server': '',
        'port': '',
        'protocol': 'http',
    },
    'Advanced': {
        'socket-timeout': '20',
        'show-user-avatars': 'on',
    },
    'Window': {
        'size': '320,480',
    },
}

ACCOUNT_CFG = {
    'OAuth':{
        'key': '',
        'secret': '',
    },
    'Login':{
        'username': '',
        'protocol': '',
    }
}

USERDIR = os.path.expanduser('~')
BASEDIR = os.path.join(USERDIR, '.config', 'turpial')

class ConfigBase:
    """Base configuration"""
    def __init__(self, default=None):
        self.__config = {}
        if default is None:
            self.default = APP_CFG
        else:
            self.default = default
        self.cfg = ConfigParser.ConfigParser()
        self.filepath = ''
        self.extra_sections = {}

    def register_extra_option(self, section, option, default_value):
        if not self.extra_sections.has_key(section):
            self.extra_sections[section] = {}
        self.extra_sections[section][option] = default_value
        self.write(section, option, default_value)

    def create(self):
        for section, v in self.default.iteritems():
            for option, value in self.default[section].iteritems():
                self.write(section, option, value)

    def load(self):
        self.__config = dict(self.default)
        self.__config.update(self.extra_sections)

        on_disk = {}

        self.cfg.read(self.configpath)

        for section in self.cfg.sections():
            if not on_disk.has_key(section):
                on_disk[section] = {}

            for option in self.cfg.options(section):
                on_disk[section][option] = self.cfg.get(section, option)

        self.__config.update(on_disk)

        # ConfigParser doesn't store on disk empty sections, so we need to remove them
        # just to compare against saved on disk
        on_memory = dict(self.__config)
        for key in on_memory.keys():
            if on_memory[key] == {}:
                del on_memory[key]

        if on_disk != on_memory:
            self.save()


    def load_failsafe(self):
        self.__config = self.default

    def save(self, config=None):
        if config is None:
            config = dict(self.__config)

        self.__config = {}
        for section, _v in config.iteritems():
            for option, value in config[section].iteritems():
                self.write(section, option, value)

    def write(self, section, option, value):
        if not self.__config.has_key(section):
            self.__config[section] = {}

        self.__config[section][option] = value

        _fd = open(self.configpath, 'w')
        if not self.cfg.has_section(section):
            self.cfg.add_section(section)
        self.cfg.set(section, option, value)
        self.cfg.write(_fd)
        _fd.close()

    def write_section(self, section, items):
        if self.cfg.has_section(section):
            self.cfg.remove_section(section)
            self.__config[section] = {}

        for option, value in items.iteritems():
            self.write(section, option, value)

    # WARN: Next version boolean will be the default answer
    def read(self, section, option, boolean=False):
        try:
            value = self.__config[section][option]
            if boolean:
                if value == 'on':
                    return True
                elif value == 'off':
                    return False
                else:
                    return value
            else:
                return value
        except Exception:
            return None

    def read_section(self, section):
        #self.log.debug('Reading section %s' % section)
        try:
            return self.__config[section]
        except Exception:
            return None

    def read_all(self):
        self.log.debug('Reading all')
        try:
            return self.__config
        except Exception:
            return None

class AppConfig(ConfigBase):
    """ Handle app configuration """
    def __init__(self):
        ConfigBase.__init__(self)
        self.log = logging.getLogger('AppConfig')
        self.log.debug('Started')
        self.basedir = BASEDIR

        self.configpath = os.path.join(self.basedir, 'config')
        self.filterpath = os.path.join(self.basedir, 'filtered')
        self.friendspath = os.path.join(self.basedir, 'friends')

        if not os.path.isdir(self.basedir):
            os.makedirs(self.basedir)
        if not os.path.isfile(self.configpath):
            self.create()
        if not os.path.isfile(self.filterpath):
            open(self.filterpath, 'w').close()
        if not os.path.isfile(self.friendspath):
            open(self.friendspath, 'w').close()

        self.log.debug('CONFIG_FILE: %s' % self.configpath)
        self.log.debug('FILTERS_FILE: %s' % self.filterpath)
        self.log.debug('FRIENDS_FILE: %s' % self.friendspath)

        self.load()

    def load_filters(self):
        muted = []
        _fd = open(self.filterpath, 'r')
        for line in _fd:
            if line == '\n':
                continue
            muted.append(line.strip('\n'))
        _fd.close()
        return muted

    def save_filters(self, filter_list):
        _fd = open(self.filterpath, 'w')
        for expression in filter_list:
            _fd.write(expression + '\n')
        _fd.close()

    def append_filter(self, expression):
        for term in self.load_filters():
            if term == expression:
                raise ExpressionAlreadyFiltered
        _fd = open(self.filterpath, 'a')
        _fd.write(expression + '\n')
        _fd.close()

    def remove_filter(self, expression):
        new_list = []
        for term in self.load_filters():
            if term == expression:
                continue
            new_list.append(term)
        self.save_filters(new_list)

    def load_friends(self):
        friends = []
        _fd = open(self.friendspath, 'r')
        for line in _fd:
            if line == '\n':
                continue
            friends.append(line.strip('\n'))
        _fd.close()
        return friends

    def save_friends(self, lst):
        _fd = open(self.friendspath, 'w')
        for friend in lst:
            _fd.write(friend + '\n')
        _fd.close()

    def get_stored_accounts(self):
        accounts = []
        acc_dir = os.path.join(BASEDIR, 'accounts')
        for root, dirs, files in os.walk(acc_dir):
            for acc_dir in dirs:
                filepath = os.path.join(root, acc_dir, 'config')
                if os.path.isfile(filepath):
                    accounts.append(acc_dir)
        return accounts

    def get_stored_columns(self):
        stored_cols = self.read_section('Columns')
        indexes = stored_cols.keys()
        indexes.sort()
        columns = []

        for i in indexes:
            value = stored_cols[i]
            if value != '':
                columns.append(value)
        return columns

    def delete(self):
        os.remove(self.configpath)
        self.log.debug('Deleted current config. Please restart Turpial')

class AccountConfig(ConfigBase):

    def __init__(self, account_id):
        ConfigBase.__init__(self, default=ACCOUNT_CFG)
        self.log = logging.getLogger('AccountConfig')
        self.basedir = os.path.join(BASEDIR, 'accounts', account_id)

        if XDG_CACHE:
            cachedir = BaseDirectory.xdg_cache_home
            self.imgdir = os.path.join(cachedir, 'turpial', account_id, 'images')
        else:
            self.imgdir = os.path.join(self.basedir, 'images')

        self.configpath = os.path.join(self.basedir, 'config')

        self.log.debug('CACHEDIR: %s' % self.imgdir)
        self.log.debug('CONFIGFILE: %s' % self.configpath)

        if not os.path.isdir(self.basedir):
            os.makedirs(self.basedir)
        if not os.path.isdir(self.imgdir):
            os.makedirs(self.imgdir)
        if not self.exists(account_id):
            self.create()

        try:
            self.load()
        except Exception, exc:
            self.load_failsafe()

        if not self.exists(account_id):
            self.write('Login', 'username', get_username_from(account_id))
            self.write('Login', 'protocol', get_protocol_from(account_id))

    @staticmethod
    def exists(account_id):
        basedir = os.path.join(BASEDIR, 'accounts', account_id)
        configpath = os.path.join(basedir, 'config')

        if not os.path.isfile(configpath):
            return False
        return True


    # DEPRECATE: Remove verifier in the next stable version
    def save_oauth_credentials(self, key, secret, verifier=None):
        self.write('OAuth', 'key', key)
        self.write('OAuth', 'secret', secret)

    # DEPRECATE: Remove verifier in the next stable version
    def load_oauth_credentials(self):
        key = self.read('OAuth', 'key')
        secret = self.read('OAuth', 'secret')
        if key and secret:
            return key, secret
        else:
            raise EmptyOAuthCredentials

    def forget_oauth_credentials(self):
        self.write('OAuth', 'key', '')
        self.write('OAuth', 'secret', '')

    def transform(self, pw, us):
        a = base64.b16encode(pw)
        b = us[0] + a + ('%s' % us[-1])
        c = base64.b32encode(b)
        d = ('%s' % us[-1]) + c + us[0]
        e = base64.b64encode(d)
        f = [e[i] for i in range(len(e))]
        f.reverse()
        return ''.join(f)

    def revert(self, pw, us):
        if pw == '':
            return None
        z = [pw[i] for i in range(len(pw))]
        z.reverse()
        y = ''.join(z)
        x = base64.b64decode(y)
        w = ('%s' % x[1:len(x)])[:-1]
        v = base64.b32decode(w)
        u = ('%s' % v[:len(v) - 1])[1:]
        return base64.b16decode(u)

    def dismiss(self):
        if os.path.isdir(self.imgdir):
            shutil.rmtree(self.imgdir)
            self.log.debug('Removed cache directory')
        if os.path.isfile(self.configpath):
            os.remove(self.configpath)
            self.log.debug('Removed configuration file')
        if os.path.isdir(self.basedir):
            shutil.rmtree(self.basedir)
            self.log.debug('Removed base directory')

    def delete_cache(self):
        for root, dirs, files in os.walk(self.imgdir):
            for f in files:
                path = os.path.join(root, f)
                self.log.debug("Deleting %s" % path)
                os.remove(path)

    def calculate_cache_size(self):
        size = 0
        for root, dirs, files in os.walk(self.imgdir):
            for f in files:
                path = os.path.join(root, f)
                size += os.path.getsize(path)
        return size
