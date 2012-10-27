# -*- coding: utf-8 -*-

# Global values/constants for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 07, 2011

import re

STATUSPP = 20
ARG_SEP = '-%&%-'

OS_LINUX = 'linux'
OS_WINDOWS = 'windows'
OS_MAC = 'darwin'
OS_JAVA = 'java'
OS_UNKNOWN = 'unknown'

HASHTAG_PATTERN = re.compile('(?<![\w])#[\wáéíóúÁÉÍÓÚñÑçÇ]+')
MENTION_PATTERN = re.compile('(?<![\w])@[\w]+')
CLIENT_PATTERN = re.compile('<a href="(.*?)">(.*?)</a>')
# According to RFC 3986 - http://www.ietf.org/rfc/rfc3986.txt
URL_PATTERN = re.compile('((?<!\w)(http://|ftp://|https://|www\.)[-\w._~:/?#\[\]@!$%&\'()*+,;=]*)')


class ProtocolType:
    TWITTER = 'twitter' #: Twitter
    IDENTICA = 'identica' #: Identica


class StatusColumn:
    TIMELINE = 'timeline'
    REPLIES = 'replies'
    DIRECTS = 'directs'
    FAVORITES = 'favorites'
    PUBLIC = 'public'
    SENT = 'sent'
    CONVERSATION = 'conversation'
    PROFILE = 'profile'
    SINGLE = 'single'


class StatusType:
    NORMAL = 0x1
    DIRECT = 0x2


class ColumnType:
    TIMELINE = 'timeline'
    REPLIES = 'replies'
    DIRECTS = 'directs'
    SENT = 'sent'
    FAVORITES = 'favorites'
    PUBLIC = 'public'


class LoginStatus:
    NONE = 0
    DONE = 1
    IN_PROGRESS = 2

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

    900: "Feature not implemented yet",
    999: "Unknown error",
}
