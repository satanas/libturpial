# -*- coding: utf-8 -*-


class EmptyOAuthCredentials(Exception):
    pass

class EmptyBasicCredentials(Exception):
    pass

class AccountAlreadyExists(Exception):
    pass

class ErrorCreatingAccount(Exception):
    pass

class ErrorLoadingAccount(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

class AccountNotLoggedIn(Exception):
    pass

class AccountSuspended(Exception):
    pass

class StatusMessageTooLong(Exception):
    pass

class StatusDuplicated(Exception):
    pass

class ResourceNotFound(Exception):
    pass

class ServiceOverCapacity(Exception):
    pass

class InternalServerError(Exception):
    pass

class ServiceDown(Exception):
    pass

class InvalidOrMissingCredentials(Exception):
    pass

class BadOAuthTimestamp(Exception):
    pass

class ErrorSendingDirectMessage(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

class RateLimitExceeded(Exception):
    pass

class InvalidOAuthToken(Exception):
    pass

class URLShortenError(Exception):
    """An URL shorten error ocurred"""
    def __init__(self, message):
        self.message = message


class NoURLException(Exception):
    """No URL to short"""
    def __init__(self):
        self.message = 'No URL to short'


class AlreadyShortURLException(Exception):
    """URL already short"""
    def __init__(self):
        self.message = 'URL already short'


class UploadImageError(Exception):
    """An upload image error ocurred"""
    def __init__(self, message):
        self.message = message

class NotSupported(Exception):
    pass
