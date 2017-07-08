import mock
import datetime

from tests import TestCaseBase

from auth_core.entities import AuthUser, AuthLogin
from auth_core.appengine_tools import get_resource_id_from_key
from auth_core.api import access_tokens as access_tokens_api
from auth_core.errors import AuthenticationError


class CreateAccessTokenTests(TestCaseBase):
    def test_simple(self):
        # Test to ensure that we can generate a JWT and it contains 2 separators
        access_token = access_tokens_api.create_access_token({})
        self.assertEqual(access_token.count('.'), 2)

    @mock.patch('auth_core.api.access_tokens._make_expiration_date')
    @mock.patch('auth_core.api.access_tokens.datetime')
    @mock.patch('auth_core.api.access_tokens.jwt')
    def test_mocked(self, m_jwt, m_datetime, m_expiration):

        expected_iat = mock.Mock(name='mock_utcnow')
        expected_exp = mock.Mock(name='mock_later')
        m_datetime.datetime.utcnow.return_value = expected_iat
        m_expiration.return_value = expected_exp

        result = access_tokens_api.create_access_token({'foo': 'bar'})
        self.assertEqual(result, m_jwt.encode.return_value)

        claims = {'iss': 'jwt_issuer',
                  'iat': expected_iat,
                  'data': {'foo': 'bar'},
                  'aud': 'jwt_aud',
                  'exp': expected_exp
                  }
        m_jwt.encode.assert_called_once_with(*[claims, 'jwt_secret'], **{'algorithm': 'HS256'})
        m_expiration.assert_called_once_with(expected_iat, 60*60)


@mock.patch('auth_core.api.access_tokens._make_expiration_date')
@mock.patch('auth_core.api.access_tokens.datetime')
class ReadAccessTokenTests(TestCaseBase):
    def test_simple(self, m_datetime, m_expiration):
        # Setup Tests
        mock_iat = datetime.datetime.utcnow()
        mock_exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
        m_datetime.datetime.utcnow.return_value = mock_iat
        m_expiration.return_value = mock_exp

        access_token = access_tokens_api.create_access_token({'foo': 'bar'})

        # Run Code to Test
        result = access_tokens_api.read_access_token(access_token)

        # Check Results
        self.assertEquals(result, {u'foo': u'bar'})

    def test_expired(self, m_datetime, m_expiration):
        # Create a token created 60 seconds ago and expired 30 seconds ago
        mock_iat = datetime.datetime.utcnow() - datetime.timedelta(seconds=60)
        mock_exp = datetime.datetime.utcnow() - datetime.timedelta(seconds=30)
        m_datetime.datetime.utcnow.return_value = mock_iat
        m_expiration.return_value = mock_exp

        access_token = access_tokens_api.create_access_token({'foo': 'bar'})

        # Run Code to Test
        self.assertRaises(AuthenticationError, access_tokens_api.read_access_token, access_token)

    def test_bad_secret(self, m_datetime, m_expiration):
        mock_iat = datetime.datetime.utcnow()
        mock_exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
        m_datetime.datetime.utcnow.return_value = mock_iat
        m_expiration.return_value = mock_exp

        access_token = access_tokens_api.create_access_token({'foo': 'bar'})

        with mock.patch('auth_core.api.access_tokens.auth_settings') as m_settings:
            m_settings.JWT_SECRET = 'different_secret'
            self.assertRaises(AuthenticationError,
                              access_tokens_api.read_access_token,
                              access_token)


class MakeTokenUserDataDictTests(TestCaseBase):
    def test_base(self):
        # Setup Test
        user_key = AuthUser(username="testUser1").put()
        user_id = get_resource_id_from_key(user_key)

        login_key = AuthLogin(key=AuthLogin.generate_key(user_key, 'basic'),
                              auth_type='basic',
                              auth_token='hashed_password',
                              auth_data='salt',
                              user_key=user_key).put()

        # Run Code to Test
        result = access_tokens_api.make_token_user_data_dict(user_key.get(),
                                                             login_key.get(),
                                                             version=1)
        # Check Results
        self.assertDictEqual(result, {'login_type': u'basic',
                                      'version': 1,
                                      'id': user_id})


class GetUserAndLoginFromAccessTokenTests(TestCaseBase):
    def test_base(self):
        # Setup Test
        user_key = AuthUser(username="testUser1").put()
        user_id = get_resource_id_from_key(user_key)

        login_key = AuthLogin(key=AuthLogin.generate_key(user_key, 'basic'),
                              auth_type='basic',
                              auth_token='hashed_password',
                              auth_data='salt',
                              user_key=user_key).put()

        user_data = {'id': user_id, 'login_type': 'basic', 'version': 1}
        access_token = access_tokens_api.create_access_token(user_data)

        # Run Code To Test
        result = access_tokens_api.get_user_and_login_from_access_token(access_token)

        # Check results
        self.assertEquals(len(result), 2)
        self.assertTrue(isinstance(result[0], AuthUser))
        self.assertTrue(result[0].key, user_key)

        self.assertTrue(isinstance(result[1], AuthLogin))
        self.assertTrue(result[1].key, login_key)

    def test_empty_dict(self):
        access_token = access_tokens_api.create_access_token({})

        self.assertRaises(AuthenticationError, access_tokens_api.get_user_and_login_from_access_token, access_token)

    def test_invalid_user_id(self):
        user_key = AuthUser(username="testUser1").put()
        login_key = AuthLogin(key=AuthLogin.generate_key(user_key, 'basic'),
                              auth_type='basic',
                              auth_token='hashed_password',
                              auth_data='salt',
                              user_key=user_key).put()

        user_data = {'id': 'invalid', 'login_type': 'basic', 'version': 1}
        access_token = access_tokens_api.create_access_token(user_data)
        self.assertRaises(AuthenticationError, access_tokens_api.get_user_and_login_from_access_token, access_token)

    def test_invalid_login(self):
        user_key = AuthUser(username="testUser1").put()
        user_id = get_resource_id_from_key(user_key)

        login_key = AuthLogin(key=AuthLogin.generate_key(user_key, 'basic'),
                              auth_type='basic',
                              auth_token='hashed_password',
                              auth_data='salt',
                              user_key=user_key).put()

        user_data = {'id': user_id, 'login_type': 'invalid_type', 'version': 1}
        access_token = access_tokens_api.create_access_token(user_data)
        access_tokens_api.get_user_and_login_from_access_token(access_token)


class MakeExpirationDateTests(TestCaseBase):
    def test_base(self):
        dt = datetime.datetime(1982, 9, 2, 0, 0, 0)
        result = access_tokens_api._make_expiration_date(dt, 30)

        delta = result - dt
        self.assertEquals(30, delta.seconds)
