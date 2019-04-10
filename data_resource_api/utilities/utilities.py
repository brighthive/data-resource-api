"""General-purpose utilities

This module contains various data processing and support utilities.

"""

import os
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime
from alembic.config import Config
from alembic import command, autogenerate
from tableschema import Schema
from data_resource_api.db import Base, engine
from data_resource_api.config import ConfigurationFactory

# Mapping of a Frictionless Table Schema to SQLAlchemy Data Type.
#
# Note:
#   Only a subset of Table Schema elements are mapped to SQLAlchemy data types.
#   See: https://frictionlessdata.io/specs/table-schema/
TABLESCHEMA_TO_SQLALCHEMY_TYPES = {
    'string': String,
    'number': Float,
    'integer': Integer,
    'boolean': Boolean,
    'object': None,
    'array': None,
    'date': Date,
    'time': None,
    'datetime': DateTime,
    'year': None,
    'yearmonth': None,
    'duration': None,
    'geopoint': None,
    'geojson': None,
    'any': String
}


def get_app_config():
    """Convenience method for returning application configuration.

    Returns:
        Config: Configuration object based on the current application environment.

    """
    return ConfigurationFactory.from_env()


def get_sqlalchemy_type(data_type: str):
    try:
        return TABLESCHEMA_TO_SQLALCHEMY_TYPES[data_type]
    except Exception:
        return None


def create_sqlalchemy_fields(fields: dict):
    sqlalchemy_fields = {}
    for field in fields:
        sqlalchemy_fields[field['name']] = Column(
            get_sqlalchemy_type(field['type']), primary_key=True)

    return sqlalchemy_fields


def create_table_from_dict(table_schema: dict, table_name: str):
    app_config = get_app_config()
    alembic_config = Config(os.path.join(app_config.ROOT_PATH, 'alembic.ini'))
    schema = Schema(table_schema)
    if schema.valid:
        fields = create_sqlalchemy_fields(table_schema['fields'])
        fields.update({'__tablename__': table_name})
        new_class = type(table_name, (Base,), fields)
        try:
            command.revision(config=alembic_config, autogenerate=True)
            command.upgrade(config=alembic_config, revision='head')
            return new_class
        except Exception as e:
            print(e)
    else:
        print('invalid schema')
