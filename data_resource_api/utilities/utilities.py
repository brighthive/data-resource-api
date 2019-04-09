"""General-purpose utilities

This module contains various data processing and support utilities.

"""

from sqlalchemy import Column, Integer, String
from data_resource_api.db import Base, engine
from alembic.config import Config
from alembic import command, autogenerate


def create_table_from_dict():
    config = Config('../../alembic.ini')
    try:
        command.init(config=config, directory='./data_resource_api/db/migrations')
    except Exception:
        pass
    new_class = type('demo', (Base,), {
        '__tablename__': 'demos',
        'id': Column(Integer, primary_key=True),
        'thing': Column(String),
        'thing2': Column(String)
    })
    try:
        command.revision(config=config, autogenerate=True)
    except Exception:
        pass
    command.upgrade(config=config, revision="head")
    # Base.metadata.create_all(engine)
    return new_class
