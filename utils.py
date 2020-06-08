import secrets


def get_postgresql_url(**kwargs):
    return f'postgres://{kwargs["username"]}:{kwargs["password"]}@{kwargs["address"]}:{kwargs["port"]}/{kwargs["name"]}'


def get_sqlite_url(path):
    return f'sqlite:///{path}.db'


def get_django_secret_key():
    return secrets.token_urlsafe(50)
