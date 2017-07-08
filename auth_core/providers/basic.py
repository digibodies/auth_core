# Basic Username and Password Authentication

import os
import base64
from Crypto.Protocol.KDF import PBKDF2

from auth_core.errors import AuthenticationError
from auth_core.entities import AuthUser, AuthLogin

__all__ = ['get_user_by_token']

# Service specific constants - do not use externally
PBKDF2_ITERATIONS = 5000
KEY_LENGTH = 32


def get_user_by_token(token):
    """
    Given a raw token, attempt to validate it
    TODO: Rename this credential_token?
    """

    decoded_token = base64.b64decode(token)
    un, pw = decoded_token.split(':')

    user = AuthUser.query(AuthUser.username==un).get()
    if not user:
        raise AuthenticationError('Username is invalid')

    l_key = AuthLogin.generate_key(user.key, 'basic')
    login = l_key.get()

    if not validate_password(pw, login.auth_token, login.auth_data):
        raise AuthenticationError('Password is invalid')

    return user, login


def encode_password(raw_password):
    """
    Encrypt a raw password using PBKDF2 with a random salt
    returns a 2-tuple with encrypted password and salt str used
    """
    salt = os.urandom(32)
    key = PBKDF2(raw_password, salt, dkLen=KEY_LENGTH, count=PBKDF2_ITERATIONS)
    return key.encode('hex'), salt.encode('hex')


def validate_password(raw_password, encrypted_password, salt_hex):
    """
    Compare a encrypted password with a raw one

    returns boolean if password matches
    """
    salt = salt_hex.decode('hex')
    key = PBKDF2(raw_password, salt, dkLen=KEY_LENGTH, count=PBKDF2_ITERATIONS)

    return encrypted_password == key.encode('hex')


"""
def create_temp():

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
"""
