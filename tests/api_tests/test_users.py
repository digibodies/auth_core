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


class CreateUserTests(TestCaseBase):
    def test_simple(self):
        result = users_api.create_user(username='testUser1',
                                       email='test@example.com',
                                       first_name='Test',
                                       last_name='User')

        self.assertTrue(isinstance(result, AuthUser))
        self.assertEqual(result.username, 'testUser1')
        self.assertEqual(result.email, 'test@example.com')
        self.assertEqual(result.first_name, 'Test')
        self.assertEqual(result.last_name, 'User')
        # self.assertEqual(result.activated, '')

    def test_duplicate_username(self):
        """
        Ensure we blo up when there is a user with the same username
        """

        user1 = users_api.create_user(username='testUser1',
                                      email='test@example.com',
                                      first_name='Test',
                                      last_name='User')

        self.assertRaises(ValueError,
                          users_api.create_user,
                          username=user1.username,
                          email='test@example.com',
                          first_name='Test',
                          last_name='User')

