# -*- coding: utf-8 -*-

class APIExceptionManager(object):
    code_exception_map = {
            32: InvalidOrMissingCredentials,
            34: ResourceNotFound,
            64: AccountSuspended,
            88: RateLimitExceeded,
            89: InvalidOAuthToken,
            92: ProtocolNotSupported,
            130: ServiceOverCapacity,
            131: InternalServerError,
            135: BadOAuthTimestamp,
            150: ErrorSendingDirectMessage,
            186: StatusMessageTooLong,
            187: StatusMessageTooLong,
            215: InvalidOrMissingCredentials,
            401: InvalidOrMissingCredentials,
            404: ResourceNotFound,
            500: InternalServerError,
            502: ServiceDown,
            503: ServiceOverCapacity,
            504: ServiceOverCapacity
        }

    @classmethod
    def get_exception_class(cls, error_code):
        except_class = cls.code_exception_map.get(error_code, UnlistedException)
        return except_class


class EmptyOAuthCredentials(Exception):
    pass


class EmptyBasicCredentials(Exception):
    pass


class ErrorCreatingAccount(Exception):
    pass


class ErrorLoadingAccount(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class AccountNotAuthenticated(Exception):
    pass


class AccountSuspended(Exception):
    pass


class AccountAlreadyRegistered(Exception):
    pass


class ColumnAlreadyRegistered(Exception):
    pass


class StatusMessageTooLong(Exception):
    pass


class StatusDuplicated(Exception):
    pass


class ResourceNotFound(Exception):
    pass


class UserListNotFound(Exception):
    pass


class ServiceOverCapacity(Exception):
    pass


class InternalServerError(Exception):
    pass


class ServiceDown(Exception):
    pass


class InvalidOrMissingCredentials(Exception):
    pass


class InvalidOrMissingArguments(Exception):
    pass


class ExpressionAlreadyFiltered(Exception):
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

    def __init__(self, message):
        self.message = message


class NoURLToShorten(Exception):
    pass


class URLAlreadyShort(Exception):
    pass


class PreviewServiceNotSupported(Exception):
    pass


class UploadImageError(Exception):
    def __init__(self, message=None):
        self.message = message


class NotSupported(Exception):
    pass


class SSLRequired(Exception):
    pass


class UnlistedException(Exception):
    def __init__(self, data=None):
        if data:
            self.message = 'Status: %(status)s, %(message)s' % data
        else:
            self.message = 'Something went wrong'

