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


class DataManager(object):
    def __init__(self, logger_name: str = "data-manager", **kwargs):
        base = kwargs.get('base', Base)
        use_local_dirs = kwargs.get('use_local_dirs', True)
        descriptors = kwargs.get('descriptors', [])

        self.app_config = ConfigurationFactory.from_env()
        self.config = ConfigFunctions(self.app_config)

        self.db = DBHandler(self.config)

        self.orm_factory = ORMFactory(base)
        self.logger = LogFactory.get_console_logger(logger_name)

        self.descriptor_directories = []
        if use_local_dirs:
            self.descriptor_directories.append(
                self.config.get_data_resource_schema_path())

        self.custom_descriptors = descriptors

        self.data_store = []

    def monitor_data_models(self):
        """Wraps monitor data models for changes.

        Note:
            This method wraps the core worker for this class. This method has the
            responsbility of iterating through a directory to find schema files to load.
        """
        self.logger.info('Checking data models')

        # TODO this should wrap in a try except and tell us if any of the
        # properties will raise errors
        descriptors = DescriptorsGetter(
            self.descriptor_directories,
            self.custom_descriptors)
        for descriptor in descriptors.iter_descriptors():
            self.process_descriptor(descriptor)

        self.logger.info('Completed check of data models')

    def process_descriptor(self, descriptor: Descriptor):
        raise NotImplementedError("Please implement this method")

    def _process_descriptor(self, descriptor: Descriptor,
                            descriptor_exists: bool):
        """Operate on a schema dict for data model changes.

        Note:
            This method is the core worker for this class. It has the responsibility of
            monitoring all data resource models and determining if they have changed. If
            changes are detected, it also has the responsibility of building and applying
            new Alembic migrations to meet these changes. The data models will then have
            to be reconstructed by each individual worker.
        """
        try:
            self.logger.debug(f"Looking at {descriptor.file_name}")
            # Check if data model exists by checking if we have stored metadata
            # about it
            if descriptor_exists:
                self.data_model_does_exist(descriptor)
            else:
                self.data_model_does_not_exist(descriptor)

        except Exception:
            self.logger.exception(
                f"Error loading data resource schema '{descriptor.file_name}'")

    def data_model_does_exist(self, descriptor: Descriptor):
        raise NotImplementedError("Please implement this method")

    def data_model_does_not_exist(self, descriptor: Descriptor):
        raise NotImplementedError("Please implement this method")

    # Data store functions
    def data_exists(self, data_name: str, attribute_name: str):
        for data_object in self.data_store:
            if getattr(data_object, attribute_name).lower(
            ) == data_name.lower():
                return True
        return False

    def data_changed(
            self,
            data_name: str,
            checksum: str,
            name_attr: str,
            checksum_attr: str):
        for data_object in self.data_store:
            same_name = getattr(
                data_object, name_attr).lower == data_name.lower
            same_checksum = getattr(data_object, checksum_attr) != checksum
            if same_name and same_checksum:
                return True
        return False

    def get_data_index(self, data_name: str, name_attr: str):
        index = -1
        for idx, data_object in enumerate(self.data_store):
            if getattr(data_object, name_attr) == data_name.lower():
                return idx
        return index
