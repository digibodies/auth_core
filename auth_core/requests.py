from auth_core.constants import ACTIVATED_LOGIN_KEY
from auth_core.authentication import authenticate
from auth_core.entities import AnonymousAuthUser
from auth_core.errors import AuthenticationError


def mark_user_authenticated(user, login):
    """
    Modify a User so it knows it is logged in - checked via user.is_authenticated()
    """
    setattr(user, ACTIVATED_LOGIN_KEY, login)
    return user


def get_user_from_request(request):
    """
    Given a request, attempt to authenticate based on Auth Header Scheme/Credentials
    Called via the middleware, etc
    """

    # Step 1: Detect if we have an Auth Header
    raw_auth_header_val = request.headers.get('Authorization', None)
    if not raw_auth_header_val:
        return AnonymousAuthUser()

    # Step 2: Detect the Authorization type
    auth_scheme, auth_credentials = get_auth_type_and_token_from_header(raw_auth_header_val)

    # Step 3: Based on type, proceed
    user, login = authenticate(auth_scheme, auth_credentials)

    # Step 4: Activate
    return mark_user_authenticated(user, login)


def get_auth_type_and_token_from_header(raw_auth_header_val):
    """
    Return an Auth Header's Type and Token
    Input should be in the form of 'Barer token data' or 'Basic token data'
    """
    if not raw_auth_header_val:
        raise AuthenticationError("No Header Value Given")
    return raw_auth_header_val.split(' ', 1)
