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


def get_login_by_user_and_type_and_key(user_key, login_auth_type):
    """
    TODO: How do we support, say multiple twitter logins?
    """

    # TODO: Ensure known login_auth_type

    l_key = AuthLogin.generate_key(user_key, login_auth_type, )
    login = l_key.get()
    return login

"""
def create_user_temp():
    key_hex, salt_hex = basic.encode_password('fYKp?$!69+berA7z@kv3uGS#VhEB5')

    # TODO: Do this in a transaction
    un = 'utility_user'
    user = AuthUser.query(AuthUser.username==un).get()
    if (not user):
        user = AuthUser(username=un,
                        email='mhoaglund@gmail.com',
                        first_name='Utility',
                        last_name='User')

    user.is_activated = True
    user.put()

    login = AuthLogin(key=AuthLogin.generate_key(user.key, 'basic'))
    login.auth_type = 'basic'
    login.auth_token = key_hex
    login.auth_data = salt_hex
    login.user_key = user.key

    login.put()

    raise Exception("WHAAAAAAAZ?")
"""


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


def create_login(user, auth_type, auth_token, auth_data=None):
    login = AuthLogin(key=AuthLogin.generate_key(user.key, auth_type))

    if (auth_type == 'basic'):
        auth_token, auth_data = basic.encode_password(auth_token)

    login.auth_type = auth_type
    login.auth_token = auth_token
    login.auth_data = auth_data
    login.user_key = user.key

    login.put()
    return login