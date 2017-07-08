from auth_core.appengine_tools import get_key_from_resource_id

from auth_core.entities import AuthUser, AuthLogin
from auth_core.providers import basic

__all__ = ['get_user_by_id',
           'get_login_by_user_and_type_and_key',
           'create_user',
           'create_login']


def get_user_by_id(resource_id):
    """
    Resolve a user by id
    # TODO: Entity type safe get
    """
    try:
        user_key = get_key_from_resource_id(resource_id)
        return user_key.get()
    except ValueError:
        return None


def get_login_by_user_and_type_and_key(user_key, login_type, login_key):
    """
    """

    # TODO: Ensure known login_auth_type

    l_key = AuthLogin.generate_key(user_key, login_type, login_key)
    login = l_key.get()
    return login


def create_user(username, email, first_name, last_name):
    user = AuthUser.query(AuthUser.username==username).get()
    if (user):
        raise Exception("A user with this username already exists")

    user = AuthUser(username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name)

    user.is_activated = True  # TODO: Don't do this by default
    user.put()
    return user


def create_login(user, auth_type, auth_key, auth_data=None):
    """
    """

    if not auth_type == 'basic':
        raise Exception('unsupported provider')

    auth_type, auth_key, auth_data = basic.get_login_properties(user, auth_key, auth_data)
    login = AuthLogin(key=AuthLogin.generate_key(user.key, auth_type, auth_key))

    login.auth_type = auth_type
    login.auth_key = auth_key
    login.auth_data = auth_data
    login.user_key = user.key

    login.put()
    return login
