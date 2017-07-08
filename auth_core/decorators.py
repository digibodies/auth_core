"""
Simple Decorators for Auth System
"""
from auth_core.errors import PermissionException
from auth_core.requests import get_user

__all__ = ['authentication_required']


def authentication_required(handler_method):
    """
    Simple decorator to apply to rest method functions to require an authenticated user
    """
    def ensure_authenticated(self, *args, **kwargs):
        user = get_user(self.request)
        if not (user and user.is_authenticated()):
            raise PermissionException("Authentication Required")
        return handler_method(self, *args, **kwargs)

    return ensure_authenticated
