"""Data Resource Manager

The Data Resource Manager manages the lifecycles of all data resources. It is responsible for
creating the Flask application that sits at the front of the data resource.

"""
from threading import Thread
from time import sleep
from flask import Flask, make_response
from flask_restful import Api, Resource
from data_resource_api.factories import DataResourceFactory
from data_resource_api.db import Base, Session, Checksum
from data_resource_api.app.utils.exception_handler import handle_errors
from data_resource_api.app.utils.descriptor import Descriptor
from data_resource_api.app.utils.json_converter import safe_json_dumps
from data_resource_api.utils import exponential_backoff
from data_resource_api.app.data_managers.data_manager import DataManager


class DataResource(object):
    """A Data Resource

    Attributes:
        data_resource_name (str): The name of the API resource.
        api_methods (dict): The API methods and associated configurations.
        table_name (str): The name of the datastore.
        table_schema (dict): The schema of the table for validation and generation.
        api_object (object): The API object generated by the data resource manager.
        datastore_object (object): The database ORM model generated by the data resource manager.

    """

    def __init__(self):
        self.data_resource_name = None
        self.data_resource_methods = None
        self.data_resource_object = None
        self.data_model_name = None
        self.data_model_schema = None
        self.data_model_object = None
        self.checksum = None
        self.model_checksum = None


class AvailableServicesResource(Resource):
    """A Flask resource for listing available services.

    Attributes:
        endpoints (list): The collection of endpoints known to the data resource.

    """

    def __init__(self):
        self.endpoints = []

    def add_endpoint(self, new_endpoint):
        self.endpoints.append(new_endpoint)

    def get(self):
        return {'endpoints': self.endpoints}, 200


class DataResourceManagerSync(DataManager):
    """Data Resource Manager.

    Attributes:
        data_resource (list): A collection of all data resources managed by the data resouce manager.
        app_config (object): The application configuration object.

    """

    def __init__(self, **kwargs):
        super().__init__('data-resource-manager', **kwargs)

        self.data_store: DataResource = []

        self.app = None
        self.api = None
        self.available_services = AvailableServicesResource()
        self.data_resource_factory = DataResourceFactory()

    # Core functions
    def run(self, test_mode: bool = False):
        self.wait_for_db()

        def run_fn():
            self.logger.info('Data Resource Manager Running...')
            self.logger.debug(
                f"Base metadata: {list(Base.metadata.tables.keys())}")
            self.monitor_data_models()

        if test_mode:
            run_fn()
            return

        while True:
            run_fn()
            # sleep_time = 10
            sleep_time = self.config.get_sleep_interval()
            self.logger.info(
                f'Data Resource Manager Sleeping for {sleep_time} seconds...')
            sleep(sleep_time)

    def wait_for_db(self):
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
                self.logger.info('Looking for DB...')
                session = Session()
                _ = session.query(Checksum).all()
                db_active = True
                self.logger.info('Successfully connected to DB.')
            except Exception as e:
                self.logger.info('Hit exception looking for checksum...')
                # UndefinedTable
                if e.code == 'f405':
                    # TODO this is a race condition with DMM?
                    db_active = True
                    self.logger.info('Successfully connected to DB.')

                elif e.code == 'e3q8':
                    self.logger.info(
                        'Database is not available yet exception.')
                    self.logger.info(
                        'Waiting on database to become available.... {}/{}'.format(retries, max_retries))
                else:
                    self.logger.exception(f'Error occured upgrading database.')
            finally:
                session.close()

        self.logger.info('Connected to DB.')

    def create_app(self):
        """Create the base Flask application.

        Returns:
            app (object): The Flask application context.

        """
        self.app = Flask(__name__)
        self.app.config.from_object(self.app_config)
        self.api = Api(self.app)
        self.api.add_resource(self.available_services,
                              '/', endpoint='all_services_ep')
        self.app.register_error_handler(Exception, handle_errors)

        @self.api.representation('application/json')
        def output_json(data, code, headers=None):
            print("-----asdf-as-df-as-df--asd-f-adf----------")
            resp = make_response(safe_json_dumps(data), code)
            print(safe_json_dumps(data))
            resp.headers.extend(headers or {})
            return resp

        return self.app

    def process_descriptor(self, descriptor: Descriptor):
        model_exists = self.data_resource_exists(
            descriptor.data_resource_name)
        self._process_descriptor(descriptor, model_exists)

    def data_model_does_exist(self, descriptor: Descriptor):
        try:
            descriptor_file_name = descriptor.file_name
            self.logger.debug(f"Looking at {descriptor_file_name}")
            # Extract data for easier use
            data_resource_name = descriptor.data_resource_name
            table_name = descriptor.table_name
            table_schema = descriptor.table_schema
            api_schema = descriptor.api_schema

            # calculate the checksum for this json
            data_resource_checksum = descriptor.get_checksum()

            restricted_fields = descriptor.restricted_fields
            # determine if api changed
            # model = self.db.get_model_checksum(table_name) # TODO what
            # did this used to call?
            data_resource_index = self.get_data_resource_index(
                data_resource_name)
            if self.data_resource_changed(
                    data_resource_name, data_resource_checksum):
                data_resource = self.data_store[data_resource_index]
                data_resource.checksum = data_resource_checksum
                data_resource.data_resource_methods = api_schema
                data_resource.data_model_name = table_name
                data_resource.data_model_schema = table_schema
                data_resource.data_model_object = self.orm_factory.create_orm_from_dict(
                    table_schema, table_name, api_schema)
                data_resource.model_checksum = self.db.get_model_checksum(
                    table_name)
                data_resource.data_resource_object.data_model = data_resource.data_model_object
                data_resource.data_resource_object.table_schema = table_schema
                data_resource.data_resource_object.api_schema = api_schema
                data_resource.data_resource_object.restricted_fields = restricted_fields
                self.data_store[data_resource_index] = data_resource
        except Exception:
            self.logger.exception(
                'Error checking data resource')

    def data_model_does_not_exist(self, descriptor: Descriptor):
        try:
            descriptor_file_name = descriptor.file_name
            self.logger.debug(f"Looking at {descriptor_file_name}")
            # Extract data for easier use
            data_resource_name = descriptor.data_resource_name
            table_name = descriptor.table_name
            table_schema = descriptor.table_schema
            api_schema = descriptor.api_schema

            # calculate the checksum for this json
            data_resource_checksum = descriptor.get_checksum()

            restricted_fields = descriptor.restricted_fields

            data_resource = DataResource()
            data_resource.checksum = data_resource_checksum
            data_resource.data_resource_name = data_resource_name
            data_resource.data_resource_methods = api_schema
            data_resource.data_model_name = table_name
            data_resource.data_model_schema = table_schema
            data_resource.data_model_object = self.orm_factory.create_orm_from_dict(
                table_schema, table_name, api_schema)
            data_resource.model_checksum = self.db.get_model_checksum(
                table_name)
            data_resource.data_resource_object = self.data_resource_factory.create_api_from_dict(
                api_schema, 
                data_resource_name, 
                table_name, 
                self.api, data_resource.data_model_object, table_schema, restricted_fields)
            self.data_store.append(data_resource)
        except Exception:
            self.logger.exception(
                'Error checking data resource')

    # Data store functions
    def data_resource_exists(self, data_resource_name):
        """Checks if a data resource is already registered with the data resource manager.

        Args:
            data_resource_name (str): Name of the data resource.

        Returns:
            bool: True if the data resource exists. False if not.

        """
        return self.data_exists(data_resource_name, 'data_resource_name')

    def data_resource_changed(self, data_resource_name, checksum):
        """Checks if the medata for a data model has been changed.

        Args:
            data_resource_name (str): Name of the data resource.
            checksum (str): Computed MD5 checksum of the data resource schema.

        Returns:
            bool: True if the data resource has been changed. False if not.

        """
        return self.data_changed(
            data_resource_name, checksum, 'data_resource_name', 'checksum')

    def get_data_resource_index(self, data_resource_name):
        """Retrieves the index of a specific data resource in the data resources dict.

        Args:
           data_resource_name (str): Name of the data resource file on disk.

        Returns:
            int: Index of the data resource stored in memory, or -1 if not found.
        """
        return self.get_data_index(data_resource_name, 'data_resource_name')


class DataResourceManager(Thread, DataResourceManagerSync):
    def __init__(self):
        Thread.__init__(self)
        DataResourceManagerSync.__init__(self)

    def run(self):
        DataResourceManagerSync.run(self)
