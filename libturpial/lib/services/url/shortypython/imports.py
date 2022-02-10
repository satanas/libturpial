from urllib.request import urlopen, Request, HTTPRedirectHandler, build_opener
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode, quote
from urllib.parse import urlparse
from random import randint
import base64
from getpass import getpass
import re

try:
    import json
except:
    import simplejson as json
