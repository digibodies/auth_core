import base64

from tests import TestCaseBase

from auth_core.providers import basic
from auth_core.entities import AuthUser, AuthLogin
from auth_core.errors import AuthenticationError


class EncodeValidatePasswordTests(TestCaseBase):
    def test_valid(self):
        good_password = 'jive'

        # Encode Password
        result = basic.encode_password(good_password)
        self.assertEquals(len(result), 2)  # hex, salt

        # Validate Password
        is_valid = basic.validate_password(good_password, result[0], result[1])
        self.assertTrue(is_valid)

    def test_invalid(self):
        good_password = 'jive'
        bad_password = 'snakes'

        # Encode Password
        result = basic.encode_password(good_password)
        self.assertEquals(len(result), 2)  # hex, salt

        # Validate Password
        is_valid = basic.validate_password(bad_password, result[0], result[1])
        self.assertFalse(is_valid)


class GetUserByToken(TestCaseBase):
    def test_success(self):
        # Create a User
        user_key = AuthUser(username="testUser1").put()

        # Create a password
        pwkey, pwsalt = basic.encode_password('jive')

        login_key = AuthLogin(key=AuthLogin.generate_key(user_key, 'basic'),
                              auth_type='basic',
                              auth_token=pwkey,
                              auth_data=pwsalt,
                              user_key=user_key).put()

        # Create credential token
        credential_token = base64.b64encode('testUser1:jive')
        user, login = basic.get_user_by_token(credential_token)

        self.assertEquals(user_key, user.key)
        self.assertEquals(login_key, login.key)

    def test_invalid_password(self):
        # Create a User
        user_key = AuthUser(username="testUser1").put()

        # Create a password
        pwkey, pwsalt = basic.encode_password('jive')

        AuthLogin(key=AuthLogin.generate_key(user_key, 'basic'),
                  auth_type='basic',
                  auth_token=pwkey,
                  auth_data=pwsalt,
                  user_key=user_key).put()

        # Create credential token
        credential_token = base64.b64encode('testUser1:nojive')
        self.assertRaises(AuthenticationError, basic.get_user_by_token, credential_token)

    def test_user_doesnot_exist(self):
        credential_token = base64.b64encode('badguy:jive')
        self.assertRaises(AuthenticationError, basic.get_user_by_token, credential_token)
