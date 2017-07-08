from auth_core.appengine_tools import get_resource_id_from_key
from auth_core.appengine_tools import get_key_from_resource_id
from auth_core.appengine_tools import require_key_kind

from auth_core.entities import AuthUser, AuthLogin
from auth_core.providers import basic

__all__ = ['get_user_by_id',
           'get_login_by_user_and_type']


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


def create_user():
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