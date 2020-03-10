"""Data Model Manager

The Data Model Manager is responsible for managing the lifecycle of data models
for the data resource under management. It is designed to run in it's own thread,
monitoring data resources on a regular interval.

"""
from threading import Thread
from time import sleep
from data_resource_api.app.utils.descriptor import (
    Descriptor,
    DescriptorsGetter)
from data_resource_api.db import Base, Session, Checksum
from data_resource_api.utils import exponential_backoff
from data_resource_api.app.data_managers.data_manager import DataManager


class DataModelDescriptor(object):
    """A class for maintaining names and checksums for data models.

    Class Attributes:
        descriptor_file_name (str): Filename of the schema on disk.
        schema_name (str): Name of the actual database table.
        model_checksum (str): MD5 checksum for the model.

    """

    def __init__(self, descriptor_file_name=None,
                 schema_name=None, model_checksum=None):
        self.descriptor_file_name = descriptor_file_name
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

    # TODO refactor into base
    def run(self, test_mode: bool = False):
        self.initalize_base_models()

        def run_fn():
            self.logger.info('Data Model Manager Running...')
            self.monitor_data_models()

        if test_mode:  # Do not run in while loop for tests
            run_fn()
            return

        # Restore the DB state
        self.db.get_migrations_from_db_and_save_locally()
        self.load_models_from_db()
        self.db.upgrade()

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
                _ = session.query(Checksum).all()
                db_active = True
                self.logger.info('Successfully found checksum.')
            except Exception as e:
                self.logger.info('Hit exception looking for checksum...')
                # UndefinedTable
                if e.code == 'f405':
                    self.logger.info(
                        'Checksum table was not found; Running inital migration...')
                    # The migration file that describes checksums, logs, and migrations
                    # is present in the migrations folder.
                    self.db.upgrade()

                    db_active = True
                    self.logger.info('Successfully ran upgrade.')

                elif e.code == 'e3q8':
                    self.logger.info(
                        'Database is not available yet exception.')
                    self.logger.info(
                        'Waiting on database to become available.... {}/{}'.format(retries, max_retries))
                else:
                    self.logger.exception(f'Error occured upgrading database.')

        self.logger.info('Base models initalized.')

    def load_models_from_db(self) -> None:
        # Getting all remote json
        remote_descriptors = self.db.get_stored_descriptors()
        for remote_descriptor_json in remote_descriptors:
            remote_descriptor = Descriptor(remote_descriptor_json)
            self.logger.info(
                f"Loading descriptor '{remote_descriptor.table_name}' from db.")

            self.load_descriptor_into_sql_alchemy_model(
                remote_descriptor)

        self.logger.info("Loaded remote descriptors.")

    def load_descriptor_into_sql_alchemy_model(
            self, desc: Descriptor) -> None:
        _ = self.orm_factory.create_orm_from_dict(
            desc.table_schema, desc.table_name, desc.api_schema)

    def process_descriptor(self, descriptor: Descriptor):
        model_exists = self.data_model_exists(descriptor.file_name)
        self._process_descriptor(descriptor, model_exists)

    def data_model_does_exist(self, descriptor: Descriptor):
        try:
            descriptor_file_name = descriptor.file_name
            table_name = descriptor.table_name
            table_schema = descriptor.table_schema
            api_schema = descriptor.api_schema
            model_checksum = descriptor.get_checksum()

            self.logger.debug(f"{descriptor_file_name}: Found existing.")
            # check if the cached db checksum has changed from the new file
            # checksum
            if not self.data_model_changed(
                    descriptor_file_name, model_checksum):
                self.logger.debug(f"{descriptor_file_name}: Unchanged.")
                return

            self.logger.debug(f"{descriptor_file_name}: Found changed.")

            # Get the index for this descriptor within our local metadata
            data_model_index = self.get_data_model_index(
                descriptor_file_name)

            # Create the sql alchemy orm
            self.orm_factory.create_orm_from_dict(
                table_schema, table_name, api_schema)

            # Something needs to be modified
            self.db.revision(table_name, create_table=False)
            self.db.upgrade()
            self.db.update_model_checksum(
                table_name, model_checksum)

            # store metadata for descriptor locally
            self.data_store[data_model_index].model_checksum = model_checksum
        except Exception:
            self.logger.exception(
                'Error checking data model')

    def data_model_does_not_exist(self, descriptor: Descriptor):
        try:
            descriptor_file_name = descriptor.file_name
            table_name = descriptor.table_name
            table_schema = descriptor.table_schema
            api_schema = descriptor.api_schema
            model_checksum = descriptor.get_checksum()

            self.logger.debug(
                f"{descriptor_file_name}: Unseen before now.")
            # Create the metadata store for descriptor
            data_model_descriptor = DataModelDescriptor(
                descriptor_file_name, table_name, model_checksum)

            # Store the metadata for descriptor locally
            self.data_store.append(
                data_model_descriptor)
            # get the databases checksum value
            stored_checksum = self.db.get_model_checksum(
                table_name)

            # create SqlAlchemy ORM models
            _ = self.orm_factory.create_orm_from_dict(
                table_schema, table_name, api_schema)

            # if there is no checksum in the data base
            # or the database checksum does not equal this files checksum
            if stored_checksum is None or stored_checksum.model_checksum != model_checksum:
                # perform a revision
                self.db.revision(table_name)
                self.db.upgrade()
                self.db.add_model_checksum(
                    table_name, model_checksum, descriptor.descriptor)
        except Exception:
            self.logger.exception(
                'Error checking data resource')

    # Data store functions
    def data_model_exists(self, descriptor_file_name):
        """Checks if a data model is already registered with the data model manager.

        Args:
            descriptor_file_name (str): Name of the schema file on disk.

        Returns:
            bool: True if the data model exists. False if not.

        """
        return self.data_exists(descriptor_file_name, 'descriptor_file_name')

    def data_model_changed(self, descriptor_file_name, checksum):
        """Checks if the medata for a data model has been changed.

        Args:
            descriptor_file_name (str): Name of the schema file on disk.
            checksum (str): Computed MD5 checksum of the schema.

        Returns:
            bool: True if the data model has been changed. False if not.

        """
        return self.data_changed(
            descriptor_file_name, checksum, 'descriptor_file_name', 'model_checksum')

    def get_data_model_index(self, descriptor_file_name):
        """Checks if the medata for a data model has been changed.

        Args:
           descriptor_file_name (str): Name of the schema file on disk.

        Returns:
            int: Index of the schema stored in memory, or -1 if not found.
        """
        return self.get_data_index(
            descriptor_file_name, 'descriptor_file_name')


class DataModelManager(Thread, DataModelManagerSync):
    def __init__(self):
        Thread.__init__(self)
        DataModelManagerSync.__init__(self)

    def run(self):
        DataModelManagerSync.run(self)
