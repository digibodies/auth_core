# AppEngine ndb Models for Users/Authentication, etc

from google.appengine.ext import ndb


class AuthUserEntity(ndb.Model):
    """
    Persistance model representing a system user

    # TODO: Consider adding profile img
    """

    username = ndb.StringProperty()
    email = ndb.StringProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    is_activated = ndb.BooleanProperty()

    @classmethod
    def _get_kind(self):
        return 'AuthUser'

    def __repr__(self):
        """
        For easy debugging
        """

        return '<AuthUserEntity username="%s">' % (self.username)


class AuthUserMethodEntity(ndb.Model):
    """
    Storage of the various authentication records for a user

    Note: Entity keys are defined by AuthLogin.generate_key() and the user is the parent of the EG
    """
    auth_type = ndb.StringProperty()
    auth_key = ndb.StringProperty()
    auth_data = ndb.TextProperty()
    user_key = ndb.KeyProperty(kind='AuthUser') # TODO: Make this user_resource_id

    @classmethod
    def _get_kind(self):
        return 'AuthLogin'

    @staticmethod
    def generate_key_name(user_key, auth_type, auth_key):
        """
        Generate a ndb keyname for the given entity
        """
        return "%s:%s:%s" % (user_key.id(), auth_type, auth_key)

    @staticmethod
    def generate_key(user_key, auth_type, auth_key):
        key_name = AuthUserMethodEntity.generate_key_name(user_key, auth_type, auth_key)
        return ndb.Key('AuthLogin', key_name,
                       parent=user_key)
