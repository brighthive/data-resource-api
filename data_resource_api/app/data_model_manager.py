"""Data Model Manager

The Data Model Manager is responsible for managing the lifecycle of data models
for the data resource under management. It is designed to run in it's own thread,
monitoring data resources on a regular interval.

"""

import os
import json
import psycopg2
from hashlib import md5
from threading import Thread
from time import sleep
from alembic.config import Config
from alembic import command, autogenerate
from sqlalchemy.exc import ProgrammingError
from data_resource_api.factories import ORMFactory
from data_resource_api import ConfigurationFactory
from data_resource_api.factories.table_schema_types import TABLESCHEMA_TO_SQLALCHEMY_TYPES
from data_resource_api.db import Base, Session, Log, Checksum
from data_resource_api.logging import LogFactory
from data_resource_api.utils import exponential_backoff
from data_resource_api.app.descriptor import (
    Descriptor,
    DescriptorFileHelper,
    DescriptorFromFile,
    DescriptorsGetter)


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


class DataModelManagerSync(object):
    """Data Model Manager Class.

    This class extends the Thread base class and is intended to be run in its own thread.
    It will monitor the data resource schemas for changes and update the tables as needed.

    """

    def __init__(self, base: object = Base, descriptors: list = []):
        self.app_config = ConfigurationFactory.from_env()
        self.data_model_descriptors: DataModelDescriptor = []
        self.orm_factory = ORMFactory(base)
        self.logger = LogFactory.get_console_logger('data-model-manager')

        self.descriptor_directories = []
        self.descriptor_directories.append(self.get_data_resource_schema_path())
        self.custom_descriptors = descriptors

    def run(self):
        self.initalize_base_models()
        self.restore_models_from_database()

        while True:
            self.logger.info('Data Model Manager Running...')
            self.monitor_data_models()
            self.logger.info('Data Model Manager Sleeping for {} seconds...'.format(
                self.get_sleep_interval()))
            sleep(self.get_sleep_interval())

    def initalize_base_models(self):
        self.logger.info("Initalizing base models...")

        db_active = False
        max_retries = 10
        retries = 0

        exponential_time = exponential_backoff(1, 1.5)

        while not db_active and retries <= max_retries:
            if retries != 0:
                sleep_time = exponential_time()
                self.logger.info(f'Sleeping for {sleep_time} with exponential backoff...')
                sleep(sleep_time)

            retries += 1

            self.logger.info('Checking database availability...')
            try:
                self.logger.info('Looking for checksum...')
                session = Session()
                data = session.query(Checksum).all()
                db_active = True
                self.logger.info('Successfully found checksum.')
            except Exception as e:
                self.logger.info('Hit exception looking for checksum...')
                # UndefinedTable
                if e.code == 'f405':
                    self.logger.info('Checksum table was not found; Creating checksum migration...')
                    self.revision('checksum_and_logs')
                    self.upgrade()
                    db_active = True
                    self.logger.info('Successfully created checksum.')

                elif e.code == 'e3q8':
                    self.logger.info('Database is not available yet exception.')
                    self.logger.info(
                        'Waiting on database to become available.... {}/{}'.format(retries, max_retries))
                else:
                    self.logger.exception(f'Error occured upgrading database.')

        self.logger.info('Base models initalized.')

    # TODO integration test
    def restore_models_from_database(self) -> None:
        """This method will load all stored descriptor files from DB
        into SQL Alchemy ORM models.
        """
        # query database for all jsonb in checksum table
        json_descriptor_list = self.get_stored_descriptors()

        # load each item into our models
        for descriptor in json_descriptor_list:
            self.load_descriptor_into_sql_alchemy_model(descriptor)

    def load_descriptor_into_sql_alchemy_model(self, descriptor: dict) -> None:
        desc = Descriptor(descriptor)
        table_schema = desc.table_schema
        table_name = desc.table_name
        api_schema = desc.api_schema

        data_model = self.orm_factory.create_orm_from_dict(
            table_schema, table_name, api_schema)

    def get_sleep_interval(self):
        """Retrieve the thread's sleep interval.

        Returns:
            int: The sleep interval (in seconds) for the thread.

        Note:
            The method will look for an enviroment variable (SLEEP_INTERVAL).
            If the environment variable isn't set or cannot be parsed as an integer,
            the method returns the default interval of 30 seconds.

        """

        return self.app_config.DATA_MODEL_SLEEP_INTERVAL

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

    def data_model_exists(self, schema_filename):
        """Checks if a data model is already registered with the data model manager.

        Args:
            schema_filename (str): Name of the schema file on disk.

        Returns:
            bool: True if the data model exists. False if not.

        """
        exists = False
        for data_model in self.data_model_descriptors:
            if data_model.schema_filename.lower() == schema_filename.lower():
                exists = True
                break
        return exists

    def data_model_changed(self, schema_filename, checksum):
        """Checks if the medata for a data model has been changed.

        Args:
            schema_filename (str): Name of the schema file on disk.
            checksum (str): Computed MD5 checksum of the schema.

        Returns:
            bool: True if the data model has been changed. False if not.

        """
        changed = False
        for data_model in self.data_model_descriptors:
            if data_model.schema_filename.lower() == schema_filename.lower():
                if data_model.model_checksum != checksum:
                    changed = True
                break
        return changed

    def get_data_model_index(self, schema_filename):
        """Checks if the medata for a data model has been changed.

        Args:
           schema_filename (str): Name of the schema file on disk.

        Returns:
            int: Index of the schema stored in memory, or -1 if not found.
        """
        index = -1
        for idx, data_model in enumerate(self.data_model_descriptors):
            if data_model.schema_filename.lower() == schema_filename.lower():
                index = idx
                break
        return index

    def add_model_checksum(self, table_name: str, model_checksum: str = '0', descriptor_json: dict = {}):
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
            checksum.descriptor_json = descriptor_json
            session.add(checksum)
            session.commit()
        except Exception as e:
            self.logger.exception('Error adding checksum')
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
            self.logger.exception('Error updating checksum')
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
            self.logger.exception('Error retrieving checksum')
        session.close()
        return checksum

    def get_stored_descriptors(self) -> list:
        """
        Gets stored json models from database.

        Returns:
            list: List of JSON dictionaries
        """
        session = Session()
        descriptor_list = []  # list of json dict
        try:
            query = session.query(Checksum)
            for _row in query.all():
                descriptor_list.append(_row.descriptor_json)
        except Exception as e:
            self.logger.exception('Error retrieving stored models')
        session.close()

        return descriptor_list

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
            command.upgrade(config=alembic_config, revision='head')
        else:
            self.logger.info('No migrations to run...')

    def revision(self, table_name: str, create_table: bool = True):
        """Create a new migration.

        This method runs the Alembic revision command programmatically.

        """
        alembic_config, migrations_dir = self.get_alembic_config()
        if migrations_dir is not None:
            if create_table:
                message = 'Create table {}'.format(table_name)
            else:
                message = 'Update table {}'.format(table_name)
            command.revision(config=alembic_config,
                             message=message, autogenerate=True)
        else:
            self.logger.info('No migrations to run...')

    def monitor_data_models(self):
        """Wraps monitor data models for changes.

        Note:
            This method wraps the core worker for this class. This method has the
            responsbility of iterating through a directory to find schema files to load.
        """
        self.logger.info('Checking data models')

        descriptors = DescriptorsGetter(self.descriptor_directories, self.custom_descriptors)
        for descriptor in descriptors.iter_descriptors():
            self.process_descriptor(descriptor)

        self.logger.info('Completed check of data models')

    # TODO refactor this into smaller functions
    def process_descriptor(self, schema_dict: object):
        """Operate on a schema dict for data model changes.

        Note:
            This method is the core worker for this class. It has the responsibility of
            monitoring all data resource models and determining if they have changed. If
            changes are detected, it also has the responsibility of building and applying
            new Alembic migrations to meet these changes. The data models will then have
            to be reconstructed by each individual worker.
        """
        schema_filename = schema_dict.file_name
        self.logger.debug(f"Looking at {schema_filename}")

        try:
            # Extract data for easier use
            table_name = schema_dict.table_name
            table_schema = schema_dict.table_schema
            api_schema = schema_dict.api_schema

            # calculate the checksum for this json
            model_checksum = md5(
                json.dumps(
                    table_schema,
                    sort_keys=True
                ).encode('utf-8')
            ).hexdigest()

            self.logger.debug('Pre: ' + str(Base.metadata.tables.keys()))

            # Check if data model exists by checking if we have stored metadata about it
            if self.data_model_exists(schema_filename):
                self.logger.debug(f"{schema_filename}: Found existing.")
                # check if the cached db checksum has changed from the new file checksum
                if not self.data_model_changed(schema_filename, model_checksum):
                    self.logger.debug(f"{schema_filename}: Unchanged.")
                    return
                
                self.logger.debug(f"{schema_filename}: Found changed.")

                # Get the index for this descriptor within our local metadata
                data_model_index = self.get_data_model_index(
                    schema_filename)

                # Create the sql alchemy orm
                data_model = self.orm_factory.create_orm_from_dict(
                    table_schema, table_name, api_schema)
                
                # Something needs to be modified
                self.revision(table_name, create_table=False)
                self.upgrade()
                self.update_model_checksum(
                    table_name, model_checksum)
                del data_model

                self.logger.debug('Post1: ' + Base.metadata.tables.keys())

                # store metadata for descriptor locally
                self.data_model_descriptors[data_model_index].model_checksum = model_checksum

            else:
                self.logger.debug(f"{schema_filename}: Unseen before now.")
                # Create the metadata store for descriptor
                data_model_descriptor = DataModelDescriptor(
                    schema_filename, table_name, model_checksum)

                # Store the metadata for descriptor locally
                self.data_model_descriptors.append(
                    data_model_descriptor)
                # get the databases checksum value
                stored_checksum = self.get_model_checksum(
                    table_name)

                # create SqlAlchemy ORM models
                data_model = self.orm_factory.create_orm_from_dict(
                    table_schema, table_name, api_schema)

                # if there is no checksum in the data base
                # or the database checksum does not equal this files checksum
                if stored_checksum is None or stored_checksum.model_checksum != model_checksum:
                    # perform a revision
                    self.revision(table_name)
                    self.upgrade()
                    self.add_model_checksum(
                        table_name, model_checksum, schema_dict.descriptor)

                del data_model  # this can probably be removed?

                self.logger.debug('Post2: ' + str(Base.metadata.tables.keys()))

        except Exception as e:
            self.logger.exception(
                f"Error loading data resource schema '{schema_filename}'")

        self.logger.debug('Post3: ' + str(Base.metadata.tables.keys()))


class DataModelManager(Thread, DataModelManagerSync):
    def __init__(self):
        Thread.__init__(self)
        DataModelManagerSync.__init__(self)

    def run(self):
        DataModelManagerSync.run(self)
