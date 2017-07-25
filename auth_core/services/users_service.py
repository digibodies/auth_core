# Auth Public Api methods
# These methods should  check permissions, wrap in transactions, produce sideffects, etc

from google.appengine.ext import ndb
from auth_core.api import users as internal_users_api


def get_auth_users(*args, **kwargs):
    """
    Fetch a list of users
    """
    models, cursor, more = internal_users_api.query_user_models(*args, **kwargs)
    return models, cursor, more


def get_by_id(user_resource_id):
    """
    :returns: Instance of AuthModel or none
    """
    return internal_users_api.get_user_by_id(user_resource_id)


def get_by_username(username, keys_only=False):
    """"
    Query for an instance of authuser by username
    """
    return internal_users_api.get_by_username(username, keys_only)


def create_auth_user(user_data):
    """Public api method to create a new auth user

    TODO: Check request_ctx['user'] permissions
    """

    # TODO: Ensure that required props are already provided ?
    #   Do this in the internal api?

    # Check for authuser with existing username - TODO: Put this in txn(?)
    e = get_by_username(user_data['username'], keys_only=True)
    if (e):
        raise Exception("An AuthUser with username '%s' already exists" % user_data['username'])

    return _create_auth_user_txn(user_data)


# @ndb.transactional(xg=True)
def _create_auth_user_txn(user_data):
    """
    Create a new AuthUser

    TODO: Enqueue signals to update audit, etc
    """

    username = user_data.get('username')
    email = user_data.get('email')
    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')

    # Step 1: Attempt to create AuthUser
    try:
        user = internal_users_api.create_user(username, email, first_name, last_name)
    except Exception, e:
        raise Exception("Unable to create user. Original Error: " + unicode(e))
        # TODO: Return an Exception that returns a runtime error so as not to retry
    except AttributeError, e:
        raise Exception("Unable to create user. Original Error: " + unicode(e))
        # TODO: Return an Exception that returns a runtime error so as not to retry

    # Step 2:  Record Audit Logs

    # Step 3: Profit?

    return user


def update_user(user, data):
    """
    Update an existing User

    :param user: An instance of `AuthUser` Model to update
    :param user_data: A `dict` of properties to update on the `user`
    :returns: Updated `AuthUser` model
    """

    # Step 1: Ensure user exists

    # Step 2: Create diff or return user unedited

    # Step 3: Attempt to update the user
    user = _update_user_txn(user, data)
    return user


@ndb.transactional
def _update_user_txn(user, user_data):
    """
    Update an User

    :param user: An instance of `AuthUser` Model to update
    :param user_data: A `dict` of properties to update on the `user`
    :returns: Updated `AuthUser` model
    """

    # Step 1:  Record Audit Logs
    user = internal_users_api.update(user, user_data)

    # Step 2:  Record Audit Logs

    # Step 3: Profit?

    return user
