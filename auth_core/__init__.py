from auth_core.authentication import authenticate  # used as an export
from auth_core.api import access_tokens as access_tokens_api
from auth_core.requests import get_user_from_request
from core.exceptions import AuthenticationException


__all__ = ['get_access_token_for_user_and_login',
           'authenticate',
           'get_user_from_request',
           'AuthenticationException']


def get_access_token_for_user_and_login(user, login):
    """
    """

    user_payload = access_tokens_api.make_token_user_data_dict(user, login)
    return access_tokens_api.create_access_token(user_payload)  # returns a jwt token
