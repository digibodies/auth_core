from auth_core.appengine_tools import get_resource_id_from_key

from tests import TestCaseBase

from auth_core.api import users as users_api
from auth_core.internal.entities import AuthUserEntity, AuthUserMethodEntity
from auth_core.models import AuthUser

class GetUserByIdTests(TestCaseBase):
    def test_simple(self):
        user_key = AuthUserEntity(username="testUser1").put()
        user_id = get_resource_id_from_key(user_key)
        result = users_api.get_user_by_id(user_id)
        self.assertTrue(isinstance(result, AuthUser))

    def test_bad_id(self):
        self.assertIsNone(users_api.get_user_by_id('invalid_id'))


class GetLoginByUserAndType(TestCaseBase):
    def test_simple(self):
        # Setup Test
        user_key = AuthUserEntity(username="testUser1").put()
        user_id = get_resource_id_from_key(user_key)
        login_key = AuthUserMethodEntity(key=AuthUserMethodEntity.generate_key(user_key, 'basic', user_id),
                              auth_type='basic',
                              auth_key=user_id,
                              auth_data='hashed_password:salt',
                              user_key=user_key).put()

        # Run Code to Test
        result = users_api.get_login_by_user_and_type_and_key(user_key, 'basic', user_id)

        # Check Results
        self.assertTrue(isinstance(result, AuthUserMethodEntity))
        self.assertEquals(result.key, login_key)
