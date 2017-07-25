from google.appengine.datastore.datastore_query import Cursor

from auth_core.internal.entities import AuthUserEntity
from auth_core.appengine_tools import get_key_from_resource_id, get_resource_id_from_key
from auth_core.internal.entities import AuthUserMethodEntity
from auth_core.models import AuthUser
from auth_core.providers import basic

__all__ = ['get_user_by_id',
           'get_login_by_user_and_type_and_key',
           'create_user',
           'create_login']

DEFAULT_QUERY_LIMIT = 100


def get_user_by_id(resource_id):
    """
    Resolve a user by id
    # TODO: Entity type safe get
    """
    try:
        user_key = get_key_from_resource_id(resource_id)
        return _populate_model(user_key.get())
    except ValueError:
        return None


def get_login_by_user_and_type_and_key(user_key, login_type, login_key):
    """
    """

    # TODO: Ensure known login_auth_type

    l_key = AuthUserMethodEntity.generate_key(user_key, login_type, login_key)
    login = l_key.get()
    return login


def create_user(username, email, first_name, last_name):
    """
    """

    # Check for existence of user with the same username
    user = AuthUserEntity.query(AuthUserEntity.username==username).get()
    if (user):
        raise Exception("A user with this username already exists")

    # Persist to Appengine Datastore
    user = AuthUserEntity(username=username,
                          email=email,
                          first_name=first_name,
                          last_name=last_name)

    user.is_activated = True  # TODO: Don't do this by default
    user.put()

    # Convert to Domain Model
    user_model = _populate_model(user)
    return user_model


def create_login(user, auth_type, auth_key, auth_data=None):
    """
    TODO: Replace this with auth_core.api.logins.create_login
    """

    if not auth_type == 'basic':
        raise Exception('unsupported provider')

    auth_type, auth_key, auth_data = basic.get_login_properties(user, auth_key, auth_data)
    key = AuthUserMethodEntity.generate_key(user.key, auth_type, auth_key)
    login = AuthUserMethodEntity(key=key)

    login.auth_type = auth_type
    login.auth_key = auth_key
    login.auth_data = auth_data
    login.user_key = user.key

    login.put()
    return login


def query_user_models(cursor=None, *args, **kwargs):
    """
    Fetch a list of users
    #TODO:  This needs to support search, pagination, etc
    """

    # Convert opaque cursor str to native appengine cursor
    if cursor:
        kwargs['cursor'] = Cursor(urlsafe=cursor)

    entities, next_cursor, more = _query_user_entities(*args, **kwargs)

    # Hydrate models to return to service layer
    models = []
    for e in entities:
        models.append(_populate_model(e))

    # Convert native cursor to opaque str
    if next_cursor:
        next_cursor = next_cursor.urlsafe()

    return models, next_cursor, more


def get_by_username(username, keys_only=False):
    """
    Simply search for user by username
    """
    e = AuthUserEntity.query().filter(AuthUserEntity.username == username).get(keys_only=keys_only)
    if keys_only:
        if e:
            return get_resource_id_from_key(e)
        return None

    return _populate_model(e)


def _query_user_entities(limit=DEFAULT_QUERY_LIMIT, cursor=None, *args, **kwargs):
    """
    Query for preference entities
    """

    if not limit:
        limit = DEFAULT_QUERY_LIMIT

    q = AuthUserEntity.query()
    q = q.order(AuthUserEntity.username)

    entites, cursor, more = q.fetch_page(limit, start_cursor=cursor)
    return entites, cursor, more


def _populate_model(e):
    """
    """
    if not e:
        return None

    model = AuthUser()
    model.id = get_resource_id_from_key(e.key)
    model.username = e.username
    model.first_name = e.first_name
    model.last_name = e.last_name
    model.email = e.email
    return model


def _populate_entity(m):
    """
    """
    if not m:
        return None

    entity = AuthUserEntity(key=get_key_from_resource_id(m.id))
    entity.username = m.username
    entity.first_name = m.first_name
    entity.last_name = m.last_name
    entity.email = m.email
    return entity


def update(user_model, data):
    """
    Edit a User
    """
    for k, v in data.iteritems():
        setattr(user_model, k, v)

    user_entity = _populate_entity(user_model)
    user_entity.put()
    return _populate_model(user_entity)
