from rest_core.models import Model

from google.appengine.ext import ndb


class AuthUser(Model):
    """
    Domain model representing a system user
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


class AuthUserMethod(Model):
    """
    Domain model representing a user's authentication method
    """
    auth_type = ndb.StringProperty()
    auth_key = ndb.StringProperty()
    auth_data = ndb.TextProperty()
    user_resource_id = ndb.StringProperty()


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
