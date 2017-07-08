# Authentication Helpers
from auth_core.api import access_tokens as access_tokens_api
from auth_core.errors import AuthenticationError
from auth_core.providers import basic


def authenticate(auth_scheme, auth_credentials):
    """
    Given a auth_type and auth_token, attempt to authenticate
    :returns: A 2-tuple of AuthUser, AuthLogin
    """

    if (auth_scheme.lower() == 'basic'):
        # Using Basic Auth - dip into service
        return basic.get_user_by_token(auth_credentials)
    elif (auth_scheme.lower() == 'bearer'):
        # This is our internal access token
        return access_tokens_api.get_user_and_login_from_access_token(auth_credentials)
    else:
        raise AuthenticationError("Unsupported authentication type: %s" % auth_scheme)
