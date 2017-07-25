# Methods for generating and consuming JWT access tokens
import datetime
import logging
import jwt

import auth_settings
from auth_core.appengine_tools import get_resource_id_from_key
from auth_core.appengine_tools import get_key_from_resource_id


from auth_core.errors import AuthenticationError
from auth_core.api import users as users_api
from auth_core.constants import TOKEN_KEYS_V1
from auth_core.constants import JWT_ALGORITHM

__all__ = ['create_access_token',
           'read_access_token',
           'get_user_and_login_from_access_token',
           'make_token_user_data_dict']


def create_access_token(data_payload, version=1):
    """
    Create a JWT Access Token
    :param data_payload: A dict of data to encode into the token.
    :returns: A str access token
    """

    now = datetime.datetime.utcnow()
    expires = _make_expiration_date(now, auth_settings.JWT_EXPIRATION)

    jwt_payload = {
        'exp': expires,
        'aud': auth_settings.JWT_AUDIENCE,
        'iss': auth_settings.JWT_ISSUER,
        'iat': now,
        'data': data_payload
    }
    return jwt.encode(jwt_payload, auth_settings.JWT_SECRET, algorithm=JWT_ALGORITHM)


def read_access_token(access_token):
    """
    Attempt to decode the JWT Access Token
    :param access_token: A string access token
    :returns: A dict data payload encoded into the token
    """
    try:
        jwt_payload = jwt.decode(access_token,
                                 auth_settings.JWT_SECRET,
                                 algorithm=JWT_ALGORITHM,
                                 audience=auth_settings.JWT_AUDIENCE,
                                 issuer=auth_settings.JWT_ISSUER)
        return jwt_payload.get('data', {})

    except jwt.ExpiredSignatureError, e:
        # Token has expired
        logging.error("JWT Expired: " + str(e))
        raise AuthenticationError("JWT Token Expired")

    except jwt.InvalidTokenError, e:
        # Log the JWT exception for debugging
        logging.error("JWT Decode Error" + str(e))
        raise AuthenticationError("Unable to decode JWT token")


def get_user_and_login_from_access_token(access_token):
    """
    Resolve an internal AuthUser and AuthLogin for a given JWT access_token
    """
    user_data = read_access_token(access_token)

    if not user_data:
        raise AuthenticationError('Unable to get data off valid token. Version error?')

    # Get version stamp
    version = user_data.get(TOKEN_KEYS_V1.VERSION, None)
    if (version != 1):
        raise AuthenticationError('Unsupported token version: %s ' % version)

    # Get critical bits off user token
    user_id = user_data.get(TOKEN_KEYS_V1.USER_ID, None)  # i.e. resource id
    login_auth_type = user_data.get(TOKEN_KEYS_V1.LOGIN_TYPE, None)  # i.e "google"
    login_auth_key = user_data.get(TOKEN_KEYS_V1.LOGIN_KEY, None)  # i.e. google uid or user id

    # Resolve User Model
    user = users_api.get_user_by_id(user_id)

    if not user:
        raise AuthenticationError('Could not resolve user. Have they been deleted?')

    user_key = get_key_from_resource_id(user.id)

    # Resolve the active login used originally regardless of type
    if not login_auth_type:
        # How did you originally login?
        raise AuthenticationError("Could not determine login auth type from key")

    if not login_auth_key:
        # How did you originally login?
        raise AuthenticationError("Could not determine login auth key from key")

    l_key = users_api.AuthUserMethodEntity.generate_key(user_key, login_auth_type, login_auth_key)
    login = l_key.get()

    return user, login


def make_token_user_data_dict(user, login, version=1):
    """
    Create the user data dictionary for a user using v1 format
    """
    if (version != 1):
        raise Exception('Unsupported token version: %s ' % version)

    data = {
        TOKEN_KEYS_V1.VERSION: version,
        TOKEN_KEYS_V1.USER_ID: get_resource_id_from_key(user.key),
        TOKEN_KEYS_V1.LOGIN_TYPE: login.auth_type,
        TOKEN_KEYS_V1.LOGIN_KEY: login.auth_key
    }

    return data


def _make_expiration_date(dt, expiration):
    """
    Simple mockable helper to generate an expiration datetime stamp.
    :param dt: A datetime object used as a starting time timestamp
    :param expiration: Number of seconds the token is valid
    """
    return dt + datetime.timedelta(seconds=expiration)
