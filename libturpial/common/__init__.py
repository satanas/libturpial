# -*- coding: utf-8 -*-

# Global values/constants for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 07, 2011

import re

from libturpial.lib.services.media.preview import PREVIEW_MEDIA_SERVICES

NUM_STATUSES = 20

OS_LINUX = 'linux'  #: Constant to identify Linux based operating systems
OS_WINDOWS = 'windows'  #: Constant to identify Windows operating systems
OS_MAC = 'darwin'  #: Constant to identify Mac operating systems
OS_JAVA = 'java'  #: Constant to identify Java based operating systems

#: Constant to identify operating systems that does not belong to any
#: of the previous categories
OS_UNKNOWN = 'unknown'

#: Regex pattern to match microblogging hashtags (for example: #hashtags)
HASHTAG_PATTERN = re.compile('(?<![\w])#[\wáéíóúÁÉÍÓÚñÑçÇ]+')

#: Regex pattern to match microblogging mentions (for example: @user)
MENTION_PATTERN = re.compile('(?<![\w])@[\w]+')

#: Regex pattern to match client names from an <a> tag
CLIENT_PATTERN = re.compile('<a href="(.*?)">(.*?)</a>')

#: Regex pattern to match URLs
#: According to RFC 3986 - http://www.ietf.org/rfc/rfc3986.txt
URL_PATTERN = re.compile('((?<!\w)(http://|ftp://|https://|www\.)[-\w._~:/?#\[\]@!$%&\'()*+,;=]*)')

def get_username_from(account_id):
    return account_id.split('-')[0]

def get_protocol_from(account_id):
    return account_id.split('-')[1]

def get_account_id_from(column_id):
    temp = column_id.rfind('-')
    return column_id[:temp]

def build_account_id(username, protocol_id):
    return "%s-%s" % (username, protocol_id)

def get_column_slug_from(column_id):
    temp = column_id.rfind('-')
    return column_id[temp + 1:]

def get_preview_service_from_url(url):
    for service in PREVIEW_MEDIA_SERVICES:
        if PREVIEW_MEDIA_SERVICES[service].can_manage_url(url):
            return PREVIEW_MEDIA_SERVICES[service]
    return None

def is_preview_service_supported(url):
    if get_preview_service_from_url(url) is not None:
        return True
    return False

class StatusColumn:
    """Status column"""
    TIMELINE = 'timeline'  #: Timeline column
    REPLIES = 'replies'  #: Replies column
    DIRECTS = 'directs'  #: Directs column
    FAVORITES = 'favorites'  #: Favs column
    PUBLIC = 'public'  #: Public column
    SENT = 'sent'
    CONVERSATION = 'conversation'
    PROFILE = 'profile'
    SINGLE = 'single'


class ColumnType:
    """Column type"""
    TIMELINE = 'timeline'
    REPLIES = 'replies'
    DIRECTS = 'directs'
    SENT = 'sent'
    FAVORITES = 'favorites'
    PUBLIC = 'public'
    SEARCH = 'search'


ERROR_CODES = {
    100: "",
    304: "There was no new data to return",
    401: "Invalid or missing credentials",
    404: "Invalid request",
    406: "What are you trying to search?",
    420: "Wait! Your search is being too intense",

    500: "Oops! The server is broken",
    502: "Oh oh... The server is down",
    503: "The server is overloaded",

    801: "There are some network issues",
    802: "Your status was sent. Don't try again",
    803: "User is already a friend",
    804: "You've already requested to follow that user",
    805: "Invalid account",
    806: "That column doesn't exist",
    807: "Server is not responding",
    808: "Account already logged in",
    809: "Account not logged in",
    810: "SSL certificate doesn't match",
    811: "Problem shorting URL",
    812: "There are no URLs to short",
    813: "That user is not following you. You cannot send messages",
    814: "That message is too long, it looks like a testament",
    815: "URL already short",

    900: "Feature not implemented yet",
    999: "Unknown error",
}
