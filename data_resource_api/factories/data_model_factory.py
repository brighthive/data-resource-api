"""Data Model Factory

This module contains a factory object for creating database objects.

"""

import os
import hashlib
import json
from datetime import datetime
from sqlalchemy import Column, ForeignKey, MetaData
from alembic.config import Config
from alembic.context import EnvironmentContext
from alembic import command, autogenerate
from tableschema import Schema
from data_resource_api.db import Base, engine, Session, Checksum
from data_resource_api.factories.table_schema_types import TABLESCHEMA_TO_SQLALCHEMY_TYPES
from data_resource_api.config import ConfigurationFactory


class DataModelFactory(object):
    """Data model factory for generating new data resource tables."""

    def get_app_config(self):
        """Convenience method for returning application configuration.

        Returns:
            Config: Configuration object based on the current application environment.

        """
        return ConfigurationFactory.from_env()

    def get_sqlalchemy_type(self, data_type: str):
        """Convert Tableschema to SQLAlchemy type.

        Args:
            data_type (str): Tableschema type to look up in the table.

        Return:
            object: SQLAlchemy type based on Tableschema mapping.
            None: If no mapping is available.
        """
        try:
            return TABLESCHEMA_TO_SQLALCHEMY_TYPES[data_type]
        except Exception:
            return None

    def evaluate_foreign_key(self, foreign_keys, field_name, field_type):
        """Determine if a field is a foreign key.

        Args:
            foreign_keys (dict): A collection of foreign keys extracted from the
                Tableschame reference.
            field_name (str): Field to evaluate.
            field_type (str): Type of the field being evaluated.

        Note:
            This function will evaluate a field to determine if it is a foreign key.
            If the field is a foreign key, the function will determine if the table
            exists. If the table doesn't exist, the function will create the table
            with a primary key.

        Return:
            boolean, str: A flag indicating whether or not the field is a primary
                key and the name of the reference table.

        """

        for foreign_key in foreign_keys:
            if not isinstance(foreign_key['fields'], list):
                fk = [foreign_key['fields']]
            else:
                fk = foreign_key['fields']
            if field_name in fk:
                table = foreign_key['reference']['resource']
                field = foreign_key['reference']['fields']
                if not isinstance(field, list):
                    field = [field]
                foreign_key_reference = '{}.{}'.format(table, field[0])
                if table not in engine.table_names():
                    try:
                        type(table, (Base,), {
                            '__tablename__': table,
                            '__table_args__': {'extend_existing': True},
                            'id': Column(self.get_sqlalchemy_type(
                                field_type), primary_key=True)
                        })
                        self.revision(table_name=table)
                        self.upgrade()
                        session = Session()
                        table_checksum = Checksum()
                        table_checksum.data_resource = table
                        table_checksum.api_checksum = '0'
                        table_checksum.model_checksum = '0'
                        table_checksum.date_modified = datetime.utcnow()
                        session.add(table_checksum)
                        session.commit()
                        session.close()
                        return True, foreign_key_reference
                    except Exception as e:
                        return False, None
                return True, foreign_key_reference
        return False, None

    def create_sqlalchemy_fields(self, fields: dict, primary_key, foreign_keys=[]):
        """Build SQLAlchemy fields to be added to new table object.

        Args:
            fields (dict):
            primary_key (str): The primary key field.
            foreign_keys (list): Collection of foreign key fields.

        Return:
            dict: SQLAlchemy fields to append to the new database object.

        """
        sqlalchemy_fields = {}
        if isinstance(primary_key, str):
            primary_key = [primary_key]
        for field in fields:
            if 'required' in field.keys() and field['required'] is True:
                nullable = False
            else:
                nullable = True
            if field['name'] in primary_key:
                sqlalchemy_fields[field['name']] = Column(
                    self.get_sqlalchemy_type(field['type']), primary_key=True)
            else:
                is_foreign_key, reference_table = self.evaluate_foreign_key(
                    foreign_keys, field['name'], field['type'])
                if not is_foreign_key:
                    sqlalchemy_fields[field['name']] = Column(
                        self.get_sqlalchemy_type(field['type']), nullable=nullable)
                else:
                    try:
                        sqlalchemy_fields[field['name']] = Column(
                            self.get_sqlalchemy_type(
                                field['type']), ForeignKey(reference_table),
                            onupdate='CASCADE', ondelete='CASCADE')
                    except Exception as e:
                        print('An exception occured {}'.format(e))
        return sqlalchemy_fields

    def create_checksum_table(self):
        """Create the checksum table migration.

        This method will first attempt to query the checksum table and if it
        cannot be located, it will create a new migration for the table.

        """

        session = Session()
        try:
            session.query(Checksum).all()
        except Exception:
            self.revision('checksums')
            self.upgrade()
        finally:
            session.close()

    def upgrade(self):
        """Migrate up to head.

        This method runs  the Alembic upgrade command programatically.

        """
        app_config = self.get_app_config()
        alembic_config = Config(os.path.join(
            app_config.ROOT_PATH, 'alembic.ini'))
        migrations_dir = os.path.join(
            app_config.ROOT_PATH, 'migrations', 'versions')
        if os.path.exists(migrations_dir) and os.path.isdir(migrations_dir) and len(os.listdir(migrations_dir)):
            command.upgrade(config=alembic_config, revision='head')
        else:
            print('No Migrations to Run...')

    def revision(self, table_name: str):
        """Create a new migration.

        This method runs the Alembic revision command programmatically.

        """
        app_config = self.get_app_config()
        alembic_config = Config(os.path.join(
            app_config.ROOT_PATH, 'alembic.ini'))
        migrations_dir = os.path.join(
            app_config.ROOT_PATH, 'migrations', 'versions')
        if os.path.exists(migrations_dir) and os.path.isdir(migrations_dir):
            command.revision(config=alembic_config, message='Create table {}'.format(
                table_name), autogenerate=True)
        else:
            print('No Migrations to Run...')

    def create_table_from_dict(self, table_schema: dict, table_name: str):
        """Create a table from a Tableschema specification.

        Args:
            table_schema (dict): Tableschema schema as a dict.
            table_name (str): Name to assign to the table.

        """
        session = Session()
        table_checksum = hashlib.md5(json.dumps(
            table_schema).encode('utf-8')).hexdigest()
        print('********* TABLE CHECKSUM ********* {}'.format(table_checksum))
        try:
            table_metadata = session.query(Checksum).filter(
                Checksum.data_resource == table_name).first()
            if table_metadata is None:
                app_config = self.get_app_config()
                alembic_config = Config(os.path.join(
                    app_config.ROOT_PATH, 'alembic.ini'))
                schema = Schema(table_schema)
                if schema.valid:
                    if 'foreignKeys' in table_schema:
                        foreign_keys = table_schema['foreignKeys']
                    else:
                        foreign_keys = []
                    fields = self.create_sqlalchemy_fields(
                        table_schema['fields'], table_schema['primaryKey'], foreign_keys)
                    fields.update({
                        '__tablename__': table_name,
                        '__table_args__': {'extend_existing': True}
                    })
                    new_class = type(table_name, (Base,), fields)
                    session = Session()
                    table_metadata = session.query(Checksum).filter(
                        Checksum.data_resource == table_name).first()
                    if table_metadata is None:
                        checksum = Checksum()
                        checksum.data_resource = table_name
                        checksum.model_checksum = table_checksum
                        checksum.api_checksum = '0'
                        checksum.date_modified = datetime.utcnow()
                        session.add(checksum)
                        session.commit()
                        session.close()
                        self.revision(table_name)
                        self.upgrade()
                    return new_class
                else:
                    print(schema.errors)
            elif table_metadata.model_checksum == table_checksum:
                print(table_metadata.model_checksum, table_checksum)
                print('no change to table')
            else:
                app_config = self.get_app_config()
                alembic_config = Config(os.path.join(
                    app_config.ROOT_PATH, 'alembic.ini'))
                schema = Schema(table_schema)
                if schema.valid:
                    if 'foreignKeys' in table_schema:
                        foreign_keys = table_schema['foreignKeys']
                    else:
                        foreign_keys = []
                    fields = self.create_sqlalchemy_fields(
                        table_schema['fields'], table_schema['primaryKey'], foreign_keys)
                    fields.update({
                        '__tablename__': table_name,
                        '__table_args__': {'extend_existing': True}
                    })
                    new_class = type(table_name, (Base,), fields)
                print('table changed, upgrading migration....')
                self.revision(table_name)
                self.upgrade()
        except Exception as e:
            print('exception {}'.format(e))
        finally:
            session.close()
