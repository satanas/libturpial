# -*- coding: utf-8 -*-

"""Module to handle basic configuration of Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Sep 26, 2011

import os
import base64
import shutil
import logging
import ConfigParser

from libturpial.api.models.column import Column

try:
    from xdg import BaseDirectory
    XDG_CACHE = True
except:
    XDG_CACHE = False

APP_CFG = {
    'General':{
        'update-interval': '5',
        'profile-color': 'on',
        'minimize-on-close': 'on',
        'num-tweets': '60',
    },
    'Window': {
        'size': '320,480',
        'position': '-1,-1',
        'state': 'windowed',
        'visibility': 'show',
    },
    'Columns':{
    },
    'Notifications':{
        'updates': 'on',
        'login': 'on',
        'icon': 'on',
    },
    'Sounds':{
        'updates': 'on',
        'login': 'on',
    },
    'Services':{
        'shorten-url': 'is.gd',
        'upload-pic': 'TwitPic',
    },
    'Browser':{
        'cmd': ''
    },
    'Proxy':{
        'username': '',
        'password': '',
        'server': '',
        'port': '',
    },
    'Advanced': {
        'socket-timeout': '20',
        'show-user-avatars': 'on',
    },
}

ACCOUNT_CFG = {
    'OAuth':{
        'verifier': '',
        'key': '',
        'secret': '',
    },
    'Login':{
        'username': '',
        'password': '',
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
    
    def create(self):
        self.log.debug('Creating configuration file')
        _fd = open(self.configpath, 'w')
        for section, v in self.default.iteritems():
            self.cfg.add_section(section)
            for option, value in self.default[section].iteritems():
                self.cfg.set(section, option, value)
        self.cfg.write(_fd)
        _fd.close()
    
    def load(self):
        self.cfg.read(self.configpath)
        
        for section, _v in self.default.iteritems():
            if not self.__config.has_key(section):
                self.__config[section] = {}
            if not self.cfg.has_section(section): 
                self.write_section(section, self.default[section])
            if section == 'Columns':
                for item in self.cfg.items(section):
                    self.__config[section][item[0]] = item[1]
                continue
            for option, value in self.default[section].iteritems():
                if self.cfg.has_option(section, option):
                    self.__config[section][option] = self.cfg.get(section, option)
                else:
                    self.write(section, option, value)
        self.log.debug('Loaded configuration')
    
    def load_failsafe(self):
        self.__config = self.default
        self.log.debug('Loaded failsafe configuration')
    
    def save(self, config):
        self.log.debug('Saving configuration')
        _fd = open(self.configpath, 'w')
        self.__config = {}
        for section, _v in config.iteritems():
            if not self.__config.has_key(section):
                self.__config[section] = {}
            for option, value in config[section].iteritems():
                self.cfg.set(section, option, value)
                self.__config[section][option] = value
        self.cfg.write(_fd)
        _fd.close()
    
    def write(self, section, option, value):
        _fd = open(self.configpath, 'w')
        self.cfg.set(section, option, value)
        self.cfg.write(_fd)
        _fd.close()
        self.__config[section][option] = value
    
    def write_section(self, section, items):
        #self.log.debug('Writing section %s' % section)
        _fd = open(self.configpath, 'w')
        if self.cfg.has_section(section):
            self.cfg.remove_section(section)
            self.__config[section] = {}
        self.cfg.add_section(section)
        for option, value in items.iteritems():
            self.cfg.set(section, option, value)
            self.__config[section][option] = value
        self.cfg.write(_fd)
        _fd.close()
    
    def read(self, section, option):
        try:
            return self.__config[section][option]
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
        
        if not os.path.isdir(self.basedir): 
            os.makedirs(self.basedir)
        if not os.path.isfile(self.configpath): 
            self.create()
        if not os.path.isfile(self.filterpath): 
            self.create_filter_list()
        
        self.log.debug('CONFIG_FILE: %s' % self.configpath)
        self.log.debug('MUTED_FILE: %s' % self.filterpath)
        
        self.load()
        
    def create_filter_list(self):
        _fd = open(self.filterpath, 'w')
        _fd.close()
        
    def load_filters(self):
        muted = []
        _fd = open(self.filterpath, 'r')
        for line in _fd:
            if line == '\n':
                continue
            muted.append(line.strip('\n'))
        _fd.close()
        return muted
    
    def save_filters(self, lst):
        _fd = open(self.filterpath, 'w')
        for expression in lst:
            _fd.write(expression + '\n')
        _fd.close()
    
    def append_filter(self, expression):
        self.log.debug('Filtering expression: %s' % expression)
        for term in self.load_filter_list():
            if term == expression:
                self.log.debug('Expression already filtered')
                return
        _fd = open(self.filterpath, 'a')
        _fd.write(expression + '\n')
        _fd.close()
        
    def remove_filter(self, expression):
        self.log.debug('Unfiltering expression: %s' % expression)
        new_list = []
        for term in self.load_filter_list():
            if term == expression:
                continue
            new_list.append(term)
        self.save_filter_list(new_list)
    
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
                temp = value.rfind('-')
                acc_id = value[:temp]
                pt_id = acc_id.split('-')[1]
                col_id = value[temp + 1:]
                id_ = "%s-%s" % (acc_id, col_id)
                columns.append(Column(id_, acc_id, pt_id, col_id))
        return columns
    
    def save_account(self, account):
        pass

class AccountConfig(ConfigBase):
    
    def __init__(self, account_id, pw=None):
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
        
        exist = True
        if not os.path.isdir(self.basedir):
            os.makedirs(self.basedir)
        if not os.path.isdir(self.imgdir):
            os.makedirs(self.imgdir)
        if not os.path.isfile(self.configpath):
            self.create()
            exist = False
            
        try:
            self.load()
        except Except, exc:
            self.load_failsafe()
        
        if not exist:
            us = account_id.split('-')[0]
            pt = account_id.split('-')[1]
            self.write('Login', 'username', us)
            self.write('Login', 'protocol', pt)
            self.remember(pw, us)
    
    def remember(self, pw, us):
        self.write('Login', 'password', self.transform(pw, us))
    
    def forget(self):
        self.write('Login', 'password', '')
        
    def transform(self, pw, us):
        a = base64.b16encode(pw)
        b = us[0] + a + ('%s' % us[-1])
        c = base64.b32encode(b)
        d = ('%s' % us[-1]) + c + us[0]
        e = base64.b64encode(d)
        return e[0:len(us)]+ e[len(us):]
        
    def revert(self, pw, us):
        if pw == '':
            return None
        a = base64.b64decode(pw)
        b = a[1:-1]
        c = base64.b32decode(b)
        d = c[1:-1]
        e = base64.b16decode(d)
        return e[0:len(us)]+ e[len(us):]
        
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
