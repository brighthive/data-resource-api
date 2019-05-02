"""Data Model Manager

The Data Model Manager is responsible for managing the lifecycle of data models
for the data resource under management. It is designed to run in it's own thread,
monitoring data resources on a regular interval.

"""

import os
import json
from hashlib import md5
from threading import Thread
from time import sleep
from alembic.config import Config
from alembic import command, autogenerate
from data_resource_api.factories import ORMFactory
from data_resource_api import ConfigurationFactory
from data_resource_api.factories.table_schema_types import TABLESCHEMA_TO_SQLALCHEMY_TYPES
from data_resource_api.db import Session, Log, Checksum


class DataModelDescriptor(object):
    """A class for maintaining names and checksums for data models.

    Class Attributes:
        schema_filename (str): Filename of the schema on disk.
        schema_name (str): Name of the actual database table.
        model_checksum (str): MD5 checksum for the model.

    """

    def __init__(self, schema_filename=None, schema_name=None, model_checksum=None):
        self.schema_filename = schema_filename
        self.schema_name = schema_name
        self.model_checksum = model_checksum


class DataModelManager(Thread):
    """Data Model Manager Class.

    This class extends the Thread base class and is intended to be run in its own thread.
    It will monitor the data resource schemas for changes and update the tables as needed.

    """

    def __init__(self):
        Thread.__init__(self)
        self.app_config = ConfigurationFactory.from_env()
        self.data_model_descriptors: DataModelDescriptor = []
        self.orm_factory = ORMFactory()

    def run(self):
        while True:
            print('Data Model Manager Running...')
            self.monitor_data_models()
            sleep(self.get_sleep_interval())

    def get_sleep_interval(self):
        """Retrieve the thread's sleep interval.

        Returns:
            int: The sleep interval (in seconds) for the thread.

        Note:
            The method will look for an enviroment variable (SLEEP_INTERVAL).
            If the environment variable isn't set or cannot be parsed as an integer,
            the method returns the default interval of 30 seconds.

        """

        return self.app_config.DATA_RESOURCE_SLEEP_INTERVAL

    def get_data_resource_schema_path(self):
        """Retrieve the path to look for data resource specifications.

        Returns:
            str: The search path for data resource schemas.

        Note:
            The application will look for an environment variable named DATA_RESOURCE_PATH
            and if it is not found will revert to the default path (i.e. /path/to/application/schema).

        """

        return os.getenv(
            'DATA_RESOURCE_PATH', os.path.join(self.app_config.ROOT_PATH, 'schema'))

    def data_model_exists(self, data_model_name):
        """Checks if a data model is already registered with the data model manager.

        Returns:
            bool: True if the data model exists. False if not.

        """

        exists = False
        for data_model in self.data_model_descriptors:
            if data_model.schema_filename.lower() == data_model_name.lower():
                exists = True
                break
        return exists

    def data_model_changed(self, data_model_name, checksum):
        """Checks if the medata for a data model has been changed.

        Returns:
            bool: True if the data model has been changed. False if not.

        """
        changed = False
        for data_model in self.data_model_descriptors:
            if data_model.schema_filename.lower() == data_model_name.lower():
                if data_model.model_checksum != checksum:
                    changed = True
                break
        return changed

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
            print('Error adding checksum {}'.format(e))
        session.close()

    def update_model_checksum(self, table_name: str, model_checksum: str):
        """Updates a checksum for a data model.

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
            print('Error updating checksum {}'.format(e))
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
            print('Error retrieving checksum {}'.format(e))
        session.close()
        return checksum

    def get_alembic_config(self):
        """ Load the Alembic configuration.

        Returns:
            object, object: The Alembic configuration and migration directory.
        """

        try:
            alembic_config = Config(os.path.join(
                self.app_config.ROOT_PATH, 'alembic.ini'))
            migrations_dir = os.path.join(
                self.app_config.ROOT_PATH, 'migrations', 'versions')
            if not os.path.exists(migrations_dir) or not os.path.isdir(migrations_dir):
                migrations_dir = None
            return alembic_config, migrations_dir
        except Exception as e:
            return None, None

    def upgrade(self):
        """Migrate up to head.

        This method runs  the Alembic upgrade command programatically.

        """
        alembic_config, migrations_dir = self.get_alembic_config()
        if migrations_dir is not None:
            command.upgrade(config=alembic_config, revision='heads')
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

    def monitor_data_models(self):
        """Monitor data models for changes.

        Note:
            This method is the core worker for this class. It has the responsibility of
            monitoring all data resource models and determining if they have changed. If
            changes are detected, it also has the responsibility of building and applying
            new Alembic migrations to meet these changes. The data models will then have
            to be reconstructed by each individual worker.
        """
        schema_dir = self.get_data_resource_schema_path()
        if os.path.exists(schema_dir) and os.path.isdir(schema_dir):
            schemas = os.listdir(schema_dir)
            for schema in schemas:
                try:
                    with open(os.path.join(schema_dir, schema), 'r') as fh:
                        schema_dict = json.load(fh)
                    schema_filename = schema
                    table_name = schema_dict['datastore']['tablename']
                    table_schema = schema_dict['datastore']['schema']
                    model_checksum = md5(json.dumps(
                        table_schema, sort_keys=True).encode('utf-8')).hexdigest()
                    if self.data_model_exists(schema_filename):
                        if self.data_model_changed(schema_filename, model_checksum):
                            print('Changed')
                            # TODO update the schema for the new migration
                    else:
                        data_model_descriptor = DataModelDescriptor(
                            schema_filename, table_name, model_checksum)
                        self.data_model_descriptors.append(
                            data_model_descriptor)
                        stored_checksum = self.get_model_checksum(table_name)
                        if stored_checksum is None or stored_checksum.model_checksum != model_checksum:
                            data_model = self.orm_factory.create_orm_from_dict(
                                table_schema, table_name)
                            self.revision(table_name)
                            self.upgrade()
                            self.add_model_checksum(table_name, model_checksum)
                            del data_model
                except Exception as e:
                    print('Error loading data resource schema {} {}'.format(schema, e))
        else:
            print('Schema directory is missing...')
