# -*- coding: utf-8 -*-

# Global values/constants for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 07, 2011

STATUSPP = 20
ARG_SEP = '-%&%-'

class ProtocolType:
    TWITTER = 'twitter'
    IDENTICA = 'identica'

class UpdateType:
    DM = 'dm'
    STD = 'std'
    PROFILE = 'profile'

class ColumnType:
    TIMELINE = 'timeline'
    REPLIES = 'replies'
    DIRECTS = 'directs'
    SENT = 'sent'
    FAVORITES = 'favorites'

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
    808: "Accounr already logged in",
    
    900: "Feature not implemented yet",
    999: "Unknown error",
}

