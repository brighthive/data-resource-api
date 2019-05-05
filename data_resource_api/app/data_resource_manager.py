"""Data Resource Manager

The Data Resource Manager manages the lifecycles of all data resources. It is responsible for
creating the Flask application that sits at the front of the data resource.

"""

import os
import json
import hashlib
from threading import Thread
from time import sleep
from flask import Flask
from brighthive_authlib import OAuth2ProviderError
from flask_restful import Api, Resource
from data_resource_api.factories import ORMFactory, DataResourceFactory
from data_resource_api.config import ConfigurationFactory
from data_resource_api.db import engine, Base, Session


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


class DataResourceManager(Thread):
    """Data Resource Manager.

    Attributes:
        data_resource (list): A collection of all data resources managed by the data resouce manager.
        app_config (object): The application configuration object.

    """

    def __init__(self):
        Thread.__init__(self)
        self.data_resources: DataResource = []
        self.app_config = ConfigurationFactory.from_env()
        self.app = None
        self.api = None
        self.available_services = AvailableServicesResource()
        self.orm_factory = ORMFactory()
        self.data_resource_factory = DataResourceFactory()

    def run(self):
        while True:
            print('Data Resource Manager Running...')
            self.monitor_data_resources()
            sleep(self.get_sleep_interval())

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
        self.app.register_error_handler(Exception, self.handle_errors)

        return self.app

    def handle_errors(self, e):
        """Flask App Error Handler

        A generic error handler for Flask applications.

        Note:
            This error handler is essentially to ensure that OAuth 2.0 authorization errors
            are handled in an appropriate fashion. The application configuration used when
            building the application must set the PROPOGATE_EXPECTIONS environment variable to
            True in order for the exception to be propogated.

        Return:
            dict, int: The error message and associated error code.

        """
        if isinstance(e, OAuth2ProviderError):
            return json.dumps({'message': 'Access Denied'}), 401
        else:
            try:
                error_code = str(e).split(':')[0][:3].strip()
                error_text = str(e).split(':')[0][3:].strip()
                if isinstance(error_code, int):
                    return json.dumps({'error': error_text}), error_code
                else:
                    raise Exception
            except Exception as e:
                return json.dumps({'error': 'An unknown error occured'}), 400

    def get_sleep_interval(self):
        """Retrieve the thread's sleep interval.

        Note:
            The method will look for an enviroment variable (SLEEP_INTERVAL).
            If the environment variable isn't set or cannot be parsed as an integer,
            the method returns the default interval of 30 seconds.

        Returns:
            int: The sleep interval (in seconds) for the thread.

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

    def data_resource_exists(self, data_resource_name):
        """Checks if a data resource is already registered with the data resource manager.

        Args:
            data_resource_name (str): Name of the data resource.

        Returns:
            bool: True if the data resource exists. False if not.

        """
        exists = False
        for data_resource in self.data_resources:
            if data_resource.data_resource_name.lower() == data_resource_name.lower():
                exists = True
                break
        return exists

    def data_resource_changed(self, data_resource_name, checksum):
        """Checks if the medata for a data model has been changed.

        Args:
            data_resource_name (str): Name of the data resource.
            checksum (str): Computed MD5 checksum of the data resource schema.

        Returns:
            bool: True if the data resource has been changed. False if not.

        """
        changed = False
        for data_resource in self.data_resources:
            if data_resource.data_resource_name.lower() == data_resource_name.lower():
                if data_resource.checksum != checksum:
                    changed = True
                break
        return changed

    def get_data_resource_index(self, data_resource_name):
        """Retrieves the index of a specific data resource in the data resources dict.

        Args:
           data_resource_name (str): Name of the data resource file on disk.

        Returns:
            int: Index of the data resource stored in memory, or -1 if not found.
        """
        index = -1
        for idx, data_resource in enumerate(self.data_resources):
            if data_resource.data_resource_name == data_resource_name.lower():
                index = idx
                break
        return index

    def monitor_data_resources(self):
        """Monitor all data resources.
        """
        schema_dir = self.get_data_resource_schema_path()
        if os.path.exists(schema_dir) and os.path.isdir(schema_dir):
            schemas = os.listdir(schema_dir)
            for schema in schemas:
                with open(os.path.join(schema_dir, schema), 'r') as fh:
                    schema_dict = json.load(fh)
                try:
                    data_resource_checksum = hashlib.md5(json.dumps(
                        schema_dict, sort_keys=True).encode('utf-8')).hexdigest()
                    data_resource_name = schema_dict['api']['resource']
                    api_schema = schema_dict['api']['methods'][0]
                    table_name = schema_dict['datastore']['tablename']
                    table_schema = schema_dict['datastore']['schema']
                    if self.data_resource_exists(data_resource_name):
                        if self.data_resource_changed(data_resource_name, data_resource_checksum):
                            print('Changed')
                    else:
                        data_resource = DataResource()
                        data_resource.checksum = data_resource_checksum
                        data_resource.data_resource_name = data_resource_name
                        data_resource.data_resource_methods = api_schema
                        data_resource.data_model_name = table_name
                        data_resource.data_model_schema = table_schema
                        data_resource.data_model_object = self.orm_factory.create_orm_from_dict(
                            table_schema, table_name)
                        data_resource.data_resource_object = self.data_resource_factory.create_api_from_dict(
                            api_schema, data_resource_name, table_name, self.api, data_resource.data_model_object, table_schema)
                        self.data_resources.append(data_resource)
                except Exception as e:
                    print('Error loading schema {}'.format(e))
        else:
            print('Schema directory does not exist.')
