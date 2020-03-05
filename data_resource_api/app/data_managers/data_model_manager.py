"""Data Model Manager

The Data Model Manager is responsible for managing the lifecycle of data models
for the data resource under management. It is designed to run in it's own thread,
monitoring data resources on a regular interval.

"""
import sys
import json
from hashlib import md5
from threading import Thread
from time import sleep
from data_resource_api.app.utils.descriptor import (
    Descriptor,
    DescriptorsGetter)
from data_resource_api.app.utils.db_handler import DBHandler
from data_resource_api.app.utils.config import ConfigFunctions
from data_resource_api.config import ConfigurationFactory
from data_resource_api.db import Base, Session, Checksum
from data_resource_api.factories import ORMFactory
from data_resource_api.logging import LogFactory
from data_resource_api.utils import exponential_backoff
from data_resource_api.app.data_managers.data_manager import DataManager


class DataModelDescriptor(object):
    """A class for maintaining names and checksums for data models.

    Class Attributes:
        schema_filename (str): Filename of the schema on disk.
        schema_name (str): Name of the actual database table.
        model_checksum (str): MD5 checksum for the model.

    """

    def __init__(self, schema_filename=None,
                 schema_name=None, model_checksum=None):
        self.schema_filename = schema_filename
        self.schema_name = schema_name
        self.model_checksum = model_checksum


class DataModelManagerSync(DataManager):
    """Data Model Manager Class.

    This class extends the Thread base class and is intended to be run in its own thread.
    It will monitor the data resource schemas for changes and update the tables as needed.

    """

    def __init__(self, **kwargs):
        super().__init__('data-model-manager', **kwargs)
        self.data_store: DataModelDescriptor = []

    # Core functions

    def run(self, test_mode: bool = False):
        self.initalize_base_models()
        self.restore_models_from_database()

        def run_fn():
            self.logger.info('Data Model Manager Running...')
            self.monitor_data_models()

        if test_mode:  # Does not run in while loop
            run_fn()
            return

        while True:
            run_fn()
            self.logger.info('Data Model Manager Sleeping for {} seconds...'.format(
                self.config.get_sleep_interval()))
            sleep(self.config.get_sleep_interval())

    def initalize_base_models(self):
        self.logger.info("Initalizing base models...")

        db_active = False
        max_retries = 10
        retries = 0

        exponential_time = exponential_backoff(1, 1.5)

        while not db_active and retries <= max_retries:
            if retries != 0:
                sleep_time = exponential_time()
                self.logger.info(
                    f'Sleeping for {sleep_time} with exponential backoff...')
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
                    self.logger.info(
                        'Checksum table was not found; Creating checksum migration...')
                    self.db.revision('checksum_and_logs')
                    self.db.upgrade()
                    db_active = True
                    self.logger.info('Successfully created checksum.')

                elif e.code == 'e3q8':
                    self.logger.info(
                        'Database is not available yet exception.')
                    self.logger.info(
                        'Waiting on database to become available.... {}/{}'.format(retries, max_retries))
                else:
                    self.logger.exception(f'Error occured upgrading database.')

        self.logger.info('Base models initalized.')

    def print_thing(self, text, obj):
        self.logger.info(text)
        self.logger.info(json.dumps(obj, indent=4))

    # TODO integration test
    def restore_models_from_database(self) -> None:
        """This method will load all stored descriptor files from DB
        into SQL Alchemy ORM models.
        """
        # get a list of all descriptors that we are going to process locally
        # {
        #     "table_name": {
        #         "local_checksum": "",
        #         "remote_checksum": "",
        #         "local_json_descriptor": "",
        #         "loadable_json_descriptor": {}
        #     }
        # }

        descriptor_master_list = {}

        local_descriptors = DescriptorsGetter(
            self.descriptor_directories,
            self.custom_descriptors)

        # Compile local files into master list
        for local_descriptor in local_descriptors.iter_descriptors():
            local_checksum = local_descriptor.get_checksum()
            local_json_descriptor = local_descriptor.descriptor
            descriptor_master_list[local_descriptor.table_name] = {
                "local_checksum": local_checksum,
                "remote_checksum": None,
                "local_json_descriptor": local_json_descriptor,
                "loadable_json_descriptor": None
            }

        self.print_thing('loaded all local', descriptor_master_list)

        # Getting all remote json
        # presumably we want to put that json into the master list
        remote_descriptor_json = self.db.get_stored_descriptors()
        for remote_descriptor_json in remote_descriptor_json:
            remote_descriptor = Descriptor(remote_descriptor_json)

            if remote_descriptor.table_name not in descriptor_master_list:  # .keys()?
                descriptor_master_list[remote_descriptor.table_name] = {}

            # override json_descriptor
            descriptor_master_list[remote_descriptor.table_name]['loadable_json_descriptor'] = remote_descriptor.descriptor

        self.print_thing('Loaded remote json', descriptor_master_list)

        # store remote checksums into our master list
        for table_name, remote_checksum in self.db.get_stored_checksums():
            descriptor_master_list[table_name]['remote_checksum'] = remote_checksum

        self.print_thing('loaded remote checksums', descriptor_master_list)

        # find all items in master list that do not have json
        for table_name in descriptor_master_list.keys():
            loadable_json = descriptor_master_list[table_name]['loadable_json_descriptor']
            if loadable_json is not None:
                continue

            # if there is no remote checksum and no loadable that means this is
            # a new file.
            remote_checksum = descriptor_master_list[table_name]['remote_checksum']
            local_json = descriptor_master_list[table_name]['local_json_descriptor']
            if remote_checksum is None and loadable_json is None and local_json is not None:
                descriptor_master_list[table_name] = {}
                # descriptor_master_list[table_name]['loadable_json_descriptor'] = local_json
                continue

            # If the remote and local checksum match then move the
            # local descriptor to loadable descriptor field
            local_checksum = descriptor_master_list[table_name]['local_checksum']
            remote_checksum = descriptor_master_list[table_name]['remote_checksum']
            if local_checksum == remote_checksum:
                descriptor_master_list[table_name]['loadable_json_descriptor'] = descriptor_master_list[table_name]['local_json_descriptor']
                continue

            # otherwise
            # panic!!!
            raise RuntimeError(
                f"Backwards compatability error -- you must find the descriptor with the matching checksum for table '{table_name}'")
            sys.exit(1337)

        self.print_thing('Made it past panic', descriptor_master_list)

        # load each item into our models
        for table_name in descriptor_master_list.keys():
            # Assumed to be new descriptor -- process normally -- do not load
            # early
            if not descriptor_master_list[table_name]:
                continue

            self.load_descriptor_into_sql_alchemy_model(
                descriptor_master_list[table_name]['loadable_json_descriptor'])

    def load_descriptor_into_sql_alchemy_model(self, descriptor: dict) -> None:
        desc = Descriptor(descriptor)
        table_schema = desc.table_schema
        table_name = desc.table_name
        api_schema = desc.api_schema

        data_model = self.orm_factory.create_orm_from_dict(
            table_schema, table_name, api_schema)

    def monitor_data_models(self):
        """Wraps monitor data models for changes.

        Note:
            This method wraps the core worker for this class. This method has the
            responsbility of iterating through a directory to find schema files to load.
        """
        self.logger.info('Checking data models')

        descriptors = DescriptorsGetter(
            self.descriptor_directories,
            self.custom_descriptors)
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

            # Check if data model exists by checking if we have stored metadata
            # about it
            if self.data_model_exists(schema_filename):
                self.logger.debug(f"{schema_filename}: Found existing.")
                # check if the cached db checksum has changed from the new file
                # checksum
                if not self.data_model_changed(
                        schema_filename, model_checksum):
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
                self.db.revision(table_name, create_table=False)
                self.db.upgrade()
                self.db.update_model_checksum(
                    table_name, model_checksum)
                del data_model

                self.logger.debug('Post1: ' + Base.metadata.tables.keys())

                # store metadata for descriptor locally
                self.data_store[data_model_index].model_checksum = model_checksum

            else:
                self.logger.debug(f"{schema_filename}: Unseen before now.")
                # Create the metadata store for descriptor
                data_model_descriptor = DataModelDescriptor(
                    schema_filename, table_name, model_checksum)

                # Store the metadata for descriptor locally
                self.data_store.append(
                    data_model_descriptor)
                # get the databases checksum value
                stored_checksum = self.db.get_model_checksum(
                    table_name)

                # create SqlAlchemy ORM models
                data_model = self.orm_factory.create_orm_from_dict(
                    table_schema, table_name, api_schema)

                # if there is no checksum in the data base
                # or the database checksum does not equal this files checksum
                if stored_checksum is None or stored_checksum.model_checksum != model_checksum:
                    # perform a revision
                    self.db.revision(table_name)
                    self.db.upgrade()
                    self.db.add_model_checksum(
                        table_name, model_checksum, schema_dict.descriptor)

                del data_model  # this can probably be removed?

                self.logger.debug('Post2: ' + str(Base.metadata.tables.keys()))

        except Exception as e:
            self.logger.exception(
                f"Error loading data resource schema '{schema_filename}'")

        self.logger.debug('Post3: ' + str(Base.metadata.tables.keys()))

    # Data store functions
    def data_model_exists(self, schema_filename):
        """Checks if a data model is already registered with the data model manager.

        Args:
            schema_filename (str): Name of the schema file on disk.

        Returns:
            bool: True if the data model exists. False if not.

        """
        return self.data_exists(schema_filename, 'schema_filename')

    def data_model_changed(self, schema_filename, checksum):
        """Checks if the medata for a data model has been changed.

        Args:
            schema_filename (str): Name of the schema file on disk.
            checksum (str): Computed MD5 checksum of the schema.

        Returns:
            bool: True if the data model has been changed. False if not.

        """
        return self.data_changed(
            schema_filename, checksum, 'schema_filename', 'model_checksum')

    def get_data_model_index(self, schema_filename):
        """Checks if the medata for a data model has been changed.

        Args:
           schema_filename (str): Name of the schema file on disk.

        Returns:
            int: Index of the schema stored in memory, or -1 if not found.
        """
        return self.get_data_index(schema_filename, 'schema_filename')


class DataModelManager(Thread, DataModelManagerSync):
    def __init__(self):
        Thread.__init__(self)
        DataModelManagerSync.__init__(self)

    def run(self):
        DataModelManagerSync.run(self)
