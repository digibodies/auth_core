from auth_core.api import logins as logins_api
from auth_core.api import users as users_api
from auth_core.errors import DuplicateCredentials


def get_logins_for_user(user_resource_id):
    """
    """

    return logins_api.get_logins_for_user(user_resource_id)


def get_login_by_id(resource_id):
    """
    """

    login_model = logins_api.get_login_by_id(resource_id)

    # Optionally take in user and ensure user == login_model.user_resource_id
    return login_model


def create_login(user_resource_id, data):
    """
    """

    user = users_api.get_user_by_id(user_resource_id)
    auth_type = data.get('auth_type')
    auth_key = data.get('auth_key')
    auth_data = data.get('auth_data')

    # TODO: TODO: Use the api!?!?!
    login_model = logins_api.get_login_by_auth_data(user, auth_type, auth_key, auth_data)

    if login_model:
        raise DuplicateCredentials("There is already a login with these credentials")

    return logins_api.create_login(user_resource_id, auth_type, auth_key, auth_data)


def update_login(login_model, data):
    """
    """

    auth_type = data.get('auth_type')
    auth_key = data.get('auth_key')
    auth_data = data.get('auth_data')

    # TODO:Ensure that we're not trying to mutate auth_type or auth_key
    if not auth_type == login_model.auth_type:
        raise ValueError("You cannot change the auth_type")

    return logins_api.update_login(login_model.id, auth_type, auth_key, auth_data)
