# Authentication Exceptions
from core import exceptions as core_exceptions


class AuthenticationError(core_exceptions.AuthenticationException):
    """
    Base Authentication Error class
    """
    pass


class PermissionException(core_exceptions.PermissionException):
    """
    """
    pass


class DuplicateCredentials(Exception):
    """
    """
    pass
