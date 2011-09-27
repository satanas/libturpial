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

try:
    from xdg import BaseDirectory
    XDG_CACHE = True
except:
    XDG_CACHE = False

APP_CFG = {
    'Version':{
        'libturpial': '0.6.1-a1',
    },
    'General':{
        'home-update-interval': '3',
        'replies-update-interval': '10',
        'directs-update-interval': '15',
        'workspace': 'single',
        'profile-color': 'on',
        'remember-login-info': 'off',
        'minimize-on-close': 'on',
        'num-tweets': '60',
    },
    'Window': {
        'single-win-size': '320,480',
        'wide-win-size': '960,480',
        'window-single-position': '-1,-1',
        'window-wide-position': '-1,-1',
        'window-state': 'windowed',
        'window-visibility': 'show',
    },
    'Columns':{
        'column1': 'timeline',
        'column2': 'replies',
        'column3': 'directs',
    },
    'Notifications':{
        'sound': 'on',
        'login': 'on',
        'home': 'on',
        'replies': 'on',
        'directs': 'on',
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
        'url': '',
    }
}

ACCOUNT_CFG = {
    'oAuth':{
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
        self.log = logging.getLogger('Config')
    
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
        self.log.debug('Loading configuration')
        self.cfg.read(self.configpath)
        
        for section, _v in self.default.iteritems():
            if not self.__config.has_key(section):
                self.__config[section] = {}
            if not self.cfg.has_section(section): 
                self.write_section(section, self.default[section])
            for option, value in self.default[section].iteritems():
                if self.cfg.has_option(section, option):
                    self.__config[section][option] = self.cfg.get(section, option)
                else:
                    self.write(section, option, value)
        
    def load_failsafe(self):
        self.log.debug('Loading failsafe configuration')
        self.__config = self.default
        
    def save(self, config):
        self.log.debug('Saving configuration')
        _fd = open(self.configpath, 'w')
        for section, _v in config.iteritems():
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
        _fd = open(self.configpath, 'w')
        self.cfg.add_section(section)
        for option, value in items.iteritems():
            self.cfg.set(section, option, value)
            self.__config[section][option] = value
        
        self.cfg.write(_fd)
        _fd.close()
        
    def read(self, section, option):
        self.log.debug('Reading option %s:%s' % (section, option))
        try:
            return self.__config[section][option]
        except Exception:
            return None
            
    def read_section(self, section):
        self.log.debug('Reading section %s' % section)
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
        
    def load_filter_list(self):
        muted = []
        _fd = open(self.filterpath, 'r')
        for line in _fd:
            if line == '\n':
                continue
            muted.append(line.strip('\n'))
        _fd.close()
        return muted
        
    def save_filter_list(self, lst):
        _fd = open(self.filterpath, 'w')
        for user in lst:
            _fd.write(user + '\n')
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
    
    def save_account(self, account):
        pass

class AccountConfig(ConfigBase):
    
    def __init__(self, account_id, pw=None, remember=False):
        ConfigBase.__init__(self, default=ACCOUNT_CFG)
        
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
            if pw and remember:
                self.remember(pw, us)
            else:
                self.forget()
    
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
        a = base64.b64decode(pw)
        b = a[1:-1]
        c = base64.b32decode(b)
        d = c[1:-1]
        e = base64.b16decode(d)
        pwd = e[0:len(us)]+ e[len(us):]
        
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
