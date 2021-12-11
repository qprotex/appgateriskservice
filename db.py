import sqlalchemy.pool
from sqlalchemy import create_engine

from flask import current_app

engine = create_engine('sqlite://',
                    connect_args = {'check_same_thread': False},
                    poolclass = sqlalchemy.pool.StaticPool)


def get_db():
    return engine


def init_db():
    with engine.connect() as c:
        with current_app.open_resource('schema.sql') as f:
            lines = f.readlines()
            for line in lines:
                c.execute(line.decode('utf8'))


def init_app(app):
    init_db()
