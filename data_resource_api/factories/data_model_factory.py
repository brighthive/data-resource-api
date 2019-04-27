"""Data Model Factory

This module contains a factory object for creating database objects.

"""

import os
import hashlib
import json
from datetime import datetime
from sqlalchemy import Column, ForeignKey, MetaData, String
from alembic.config import Config
from alembic.context import EnvironmentContext
from alembic import command, autogenerate
from tableschema import Schema
from data_resource_api.db import Base, engine, Session, Checksum, Log
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

    def create_log_table(self):
        """Create the log table migration.

        This method will first attempt to query the log table and if it
        cannot be located, it will create a new migration for the table.

        """

        session = Session()
        try:
            session.query(Log).all()
        except Exception:
            self.revision('logs')
            self.upgrade()
        finally:
            session.close()

    def get_sqlalchemy_type(self, data_type: str):
        """Convert Tableschema to SQLAlchemy type.

        Args:
            data_type (str): Tableschema type to look up in the table.

        Return:
            object: SQLAlchemy type based on Tableschema mapping.
        """
        try:
            return TABLESCHEMA_TO_SQLALCHEMY_TYPES[data_type]
        except Exception:
            return String

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
                # generate a stub of the specific table to ensure the migration will run
                table_checksum = self.get_model_checksum(table)
                if table_checksum is None:
                    try:
                        type(table, (Base,), {
                            '__tablename__': table,
                            '__table_args__': {'extend_existing': True},
                            'id': Column(self.get_sqlalchemy_type(field_type), primary_key=True)
                        })
                        self.revision(table_name=table)
                        self.upgrade()
                        self.add_model_checksum(table)
                        return True, foreign_key_reference
                    except Exception as e:
                        print('LOG THIS -> {}'.format(e))
                        return False, None
                return True, foreign_key_reference
        return False, None

    def add_model_checksum(self, table_name: str, model_checksum: str = '0'):
        """Adds a new checksum for a data model.

        Args:
            table_name (str): Name of the table to add the checksum.
            checksum (str): Checksum value.
        """
        session = Session()
        try:
            checksum = Checksum()
            checksum.data_resource = table_name
            checksum.model_checksum = model_checksum
            checksum.api_checksum = '0'
            session.add(checksum)
            session.commit()
        except Exception as e:
            print('LOG THIS --> {}'.format(e))
        finally:
            session.close()

    def update_model_checksum(self, table_name: str, model_checksum: str):
        """Adds a new checksum for a data model.

        Args:
            table_name (str): Name of the table to add the checksum.
            checksum (str): Checksum value.

        Returns:
            bool: True if checksum was updated. False otherwise.

        """
        session = Session()
        updated = False
        try:
            checksum = session.query(Checksum).filter(
                Checksum.data_resource == table_name).first()
            checksum.model_checksum = model_checksum
            session.commit()
            updated = True
        except Exception as e:
            print('LOG THIS ----> {}'.format(e))
        finally:
            session.close()

        return updated

    def get_model_checksum(self, table_name: str):
        """Retrieves a checksum by table name.

        Args:
            table_name (str): Name of the table to add the checksum.

        Returns:
            object: The checksum object if it exists, None otherwise.

        """
        session = Session()
        checksum = None
        try:
            checksum = session.query(Checksum).filter(
                Checksum.data_resource == table_name).first()
        except Exception as e:
            print('LOG THIS ----------> {}'.format(e))
        finally:
            session.close()
        return checksum

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
                                field['type']), ForeignKey(reference_table, onupdate='CASCADE', ondelete='CASCADE'))
                    except Exception as e:
                        print('An exception occured {}'.format(e))
        return sqlalchemy_fields

    def get_alembic_config(self):
        """ Load the Alembic configuration.

        Returns:
            object, object: The Alembic configuration and migration directory.
        """

        try:
            app_config = self.get_app_config()
            alembic_config = Config(os.path.join(
                app_config.ROOT_PATH, 'alembic.ini'))
            migrations_dir = os.path.join(
                app_config.ROOT_PATH, 'migrations', 'versions')
            if not os.path.exists(migrations_dir) or not os.path.isdir(migrations_dir):
                migrations_dir = None
            return alembic_config, migrations_dir
        except Exception as e:
            print('LOG THIS {}'.format(e))
            return None, None

    def upgrade(self):
        """Migrate up to head.

        This method runs  the Alembic upgrade command programatically.

        """
        alembic_config, migrations_dir = self.get_alembic_config()
        if migrations_dir is not None:
            command.upgrade(config=alembic_config, revision='head')
        else:
            print('LOG THIS: No Migrations to Run...')

    def revision(self, table_name: str):
        """Create a new migration.

        This method runs the Alembic revision command programmatically.

        """
        alembic_config, migrations_dir = self.get_alembic_config()
        if migrations_dir is not None:
            command.revision(config=alembic_config, message='Create table {}'.format(
                table_name), autogenerate=True)
        else:
            print('LOG THIS: No Migrations to Run...')

    def create_table_from_dict(self, table_schema: dict, table_name: str):
        """Create a table from a Tableschema specification.

        Args:
            table_schema (dict): Tableschema schema as a dict.
            table_name (str): Name to assign to the table.

        """
        new_class = None
        checksum = self.get_model_checksum(table_name)
        try:
            table_checksum = hashlib.md5(json.dumps(
                table_schema).encode('utf-8')).hexdigest()
            alembic_config, migration_dir = self.get_alembic_config()
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
                if checksum is None:
                    self.revision(table_name)
                    self.upgrade()
                    self.add_model_checksum(table_name, table_checksum)
                elif checksum.model_checksum != table_checksum:
                    self.revision(table_name)
                    self.upgrade()
                    self.update_model_checksum(table_name, table_checksum)
            else:
                print('LOG THIS: Invalid Schema: {}'.format(schema.errors))
        except Exception as e:
            print('LOG THIS EXCEPTION {}'.format(e))
        finally:
            return new_class
