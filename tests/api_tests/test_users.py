from auth_core.appengine_tools import get_resource_id_from_key

from tests import TestCaseBase

from auth_core.api import users as users_api
from auth_core.entities import AuthUser, AuthLogin


class GetUserByIdTests(TestCaseBase):
    def test_simple(self):
        user_key = AuthUser(username="testUser1").put()
        user_id = get_resource_id_from_key(user_key)
        result = users_api.get_user_by_id(user_id)
        self.assertTrue(isinstance(result, AuthUser))

    def test_bad_id(self):
        self.assertIsNone(users_api.get_user_by_id('invalid_id'))


class GetLoginByUserAndType(TestCaseBase):
    def test_simple(self):
        # Setup Test
        user_key = AuthUser(username="testUser1").put()
        login_key = AuthLogin(key=AuthLogin.generate_key(user_key, 'basic'),
                              auth_type='basic',
                              auth_token='hashed_password',
                              auth_data='salt',
                              user_key=user_key).put()

        # Run Code to Test
        result = users_api.get_login_by_user_and_type_and_key(user_key, 'basic')

        # Check Results
        self.assertTrue(isinstance(result, AuthLogin))
        self.assertEquals(result.key, login_key)
