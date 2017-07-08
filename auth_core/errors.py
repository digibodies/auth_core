# Authentication Exceptions


class AuthError(Exception):
    pass


class AuthenticationError(AuthError):
    """
    Base Authentication Error class
    """
    pass


class AuthorizationError(AuthError):
    """
    """
    pass
