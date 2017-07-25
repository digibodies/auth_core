from auth_core.models import AuthUserMethod
from auth_core.appengine_tools import get_key_from_resource_id, get_resource_id_from_key
from auth_core.internal.entities import AuthUserMethodEntity
from auth_core.providers import basic


__all__ = ['get_login_by_id']


def _get_key_by_id(resource_id):
    try:
        return get_key_from_resource_id(resource_id)
    except ValueError:
        return None


def _get_entity_by_id(resource_id):
    login_key = _get_key_by_id(resource_id)
    if (login_key):
        return login_key.get()
    return None


def get_login_by_id(resource_id):
    """
    Resolve an Auth Method by id
    """
    login_entity = _get_entity_by_id(resource_id)
    if (login_entity):
        return _populate_model(login_entity)
    return None


def get_login_by_auth_data(user, auth_type, auth_key, auth_data):
    """
    """

    if not auth_type == 'basic':
        raise Exception('unsupported provider: %s' % auth_type)

    user_key = get_key_from_resource_id(user.id)
    login_key = AuthUserMethodEntity.generate_key(user_key, auth_type, auth_key=user.id)  # basic
    return _populate_model(login_key.get())


def get_logins_for_user(user_resource_id):

    # TODO: Switch this to strictly use user_resource_id
    user_key = get_key_from_resource_id(user_resource_id)

    login_entities = AuthUserMethodEntity.query(AuthUserMethodEntity.user_key==user_key).fetch(1000)

    login_models = []
    for login_entity in login_entities:
        login_models.append(_populate_model(login_entity))

    return login_models


def _populate_model(login_entity):
    """
    """
    if not login_entity:
        return None

    login_model = AuthUserMethod()
    login_model.id = get_resource_id_from_key(login_entity.key)

    login_model.auth_type = login_entity.auth_type
    login_model.auth_key = login_entity.auth_key
    login_model.auth_data = login_entity.auth_data
    login_model.user_resource_id = get_resource_id_from_key(login_entity.user_key)
    # TODO: Eventually it's just resource_id

    return login_model


def _populate_entity(login_model):
    """
    TODO: WE may no longer need this...
    """
    if not login_model:
        return None

    login_entity = AuthUserMethodEntity(key=get_key_from_resource_id(login_model.id))
    login_entity.auth_type = login_model.auth_type
    login_entity.auth_key = login_model.auth_key
    login_entity.auth_data = login_model.auth_data

    raise Exception(login_model)

    return login_entity


def create_login(user_resource_id, auth_type, auth_key, auth_data=None):
    """
    """

    # Note: Do this in a more api friendly manner....

    # TODO: Try/catch this stuff....
    user_key = get_key_from_resource_id(user_resource_id)
    user = user_key.get()

    if not auth_type == 'basic':
        raise Exception('unsupported provider: %s' % auth_type)

    # Wrap this in a service
    auth_type, auth_key, auth_data = basic.get_login_properties(user, auth_key, auth_data)
    key = AuthUserMethodEntity.generate_key(user.key, auth_type, auth_key)
    login_entity = AuthUserMethodEntity(key=key)

    login_entity.auth_type = auth_type
    login_entity.auth_key = auth_key
    login_entity.auth_data = auth_data
    login_entity.user_key = user.key  # TODO: Eventually it's just resource_id

    login_entity.put()

    login_model = _populate_model(login_entity)
    return login_model


def update_login(login_resource_id, auth_type, auth_key, auth_data=None):
    """
    """

    login_entity = _get_entity_by_id(login_resource_id)

    if not login_entity:
        raise Exception('TODO: THROW DOES NOT EXIST')

    if not auth_type == 'basic':
        raise Exception('unsupported provider: %s' % auth_type)

    # Generate new password
    user = login_entity.user_key.get()
    auth_type, auth_key, auth_data = basic.get_login_properties(user, auth_key, auth_data)

    # For kicks, does this yeild the same keyname for the entity?
    new_key = AuthUserMethodEntity.generate_key(user.key, auth_type, auth_key)

    if not login_entity.key == new_key:
        raise Exception("Bad Value Error or Bad Request --- key is different!!?!?!")

    # Update the various props
    login_entity.auth_type = auth_type
    login_entity.auth_key = auth_key
    login_entity.auth_data = auth_data

    login_entity.put()

    return _populate_model(login_entity)
