# Models for Users/Authentication, etc

from google.appengine.ext import ndb


class AuthUser(ndb.Model):
    """
    Lightweight model representing a system user
    """

    username = ndb.StringProperty()
    email = ndb.StringProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    is_activated = ndb.BooleanProperty()

    def __repr__(self):
        """
        For easy debugging
        """

        return '<AuthUser username="%s">' % (self.username)

    def get_display_name(self):
        """
        Helper Method for yeilding a nice display name
        """

        if self.first_name and self.last_name:
            return u'%s %s' % (self.first_name, self.last_name)
        else:
            return self.username

    def is_authenticated(self):
        """
        This is set in the middleware helper
        """
        return hasattr(self, '_active_login') and self._active_login


class AuthLogin(ndb.Model):
    """
    Storage of the various authentication records for a user

    Note: Entity keys are defined by AuthLogin.generate_key() and the user is the parent of the EG
    """
    auth_type = ndb.StringProperty()
    auth_key = ndb.StringProperty()
    auth_data = ndb.TextProperty()
    user_key = ndb.KeyProperty(kind=AuthUser)

    @staticmethod
    def generate_key_name(user_key, auth_type, auth_key):
        # TODO: Check for valid auth_type
        # TODO: Check arg types
        return "%s:%s:%s" % (user_key.id(), auth_type, auth_key)

    @staticmethod
    def generate_key(user_key, auth_type, auth_key):
        return ndb.Key('AuthLogin', AuthLogin.generate_key_name(user_key, auth_type, auth_key),
                       parent=user_key)


class AnonymousAuthUser(object):
    """
    AuthUser-like interface for non authenticated users
    This should be kept in sync with AuthUser so they can be generally used
    with the same interface

    TODO: Think about how we'll keep track of authenticated people who just
        don't have users in our system - social logins, etc
    """

    username = None
    email = None
    first_name = None
    last_name = None
    is_activated = False

    def __repr__(self):
        return u'<AnonymousAuthUser />'

    def get_display_name(self):
        return u"Guest"

    def is_authenticated(self):
        """
        An AnonymousUser can never be authenticated... otherwise they'd be an
            AuthUser
        """
        return False


class AuthUserMethod(ndb.Model):
    auth_type = ndb.StringProperty()  # GOOGLE, FACEBOOK, PASSWORD, etc
    auth_token = ndb.StringProperty()  # Whatever the token is for
    auth_data = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind=AuthUser)
    is_activate = ndb.BooleanProperty()


class AuthInvite(ndb.Model):
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    email = ndb.StringProperty()
    user_resource_id = ndb.StringProperty()
    accepted_date = ndb.DateTimeProperty()

    @property
    def is_accepted(self):
        return self.accepted_date is not None
