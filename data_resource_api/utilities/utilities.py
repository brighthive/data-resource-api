"""General-purpose utilities

This module contains various data processing and support utilities.

"""

import os
from sqlalchemy import Column, Integer, String
from alembic.config import Config
from alembic import command, autogenerate
from data_resource_api.db import Base, engine
from data_resource_api.config import ConfigurationFactory


def get_app_config():
    return ConfigurationFactory.from_env()


def create_table_from_dict():
    app_config = get_app_config()
    alembic_config = Config(os.path.join(app_config.ROOT_PATH, 'alembic.ini'))
    try:
        command.init(config=alembic_config, directory=os.path.join(
            app_config.ROOT_PATH, 'migrations'))
    except Exception:
        pass
    new_class = type('demo', (Base,), {
        '__tablename__': 'demos',
        'id': Column(Integer, primary_key=True),
        'thing': Column(String),
        'thing2': Column(String)
    })
    try:
        command.revision(config=alembic_config, autogenerate=True)
    except Exception as e:
        print(e)
    command.upgrade(config=alembic_config, revision="head")
    # Base.metadata.create_all(engine)
    return new_class
