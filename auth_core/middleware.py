import logging

from core.exceptions import AuthenticationException
from auth_core.requests import authenticate_user_from_request
from auth_core.errors import AuthenticationError
from auth_core.requests import set_user


class AuthenticationMiddleware(object):
    @staticmethod
    def process_request(request):
        try:
            user = authenticate_user_from_request(request)
            set_user(request, user)

        except AuthenticationError, e:
            logging.error(e)
            raise AuthenticationException("Authentication Failed")
