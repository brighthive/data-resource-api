"""Data Resource Manager

The Data Resource Manager manages the lifecycles of all data resources. It exists as a background process that
polls the filesystem for new data resource specifications and removes old ones. The Data Resource Manager is
also responsible for creating the Flask application that sits at the front of the data resource.


"""

import os
import json
import hashlib
from threading import Thread
from time import sleep
from flask import Flask
from flask_restful import Api, Resource
from data_resource_api.config import ConfigurationFactory
from data_resource_api.db import engine, Session
from data_resource_api.app import DataResource
from data_resource_api.factories import DataModelFactory, ApiFactory
from data_resource_api.logging.database_handler import DatabaseHandler


class AvailableServicesResource(Resource):
    """
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
        self.data_resources = []
        self.app_config = ConfigurationFactory.from_env()
        self.app = None
        self.api = None
        self.available_services = AvailableServicesResource()
        self.data_model_factory = DataModelFactory()
        self.api_factory = ApiFactory()

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

    def get_sleep_interval(self):
        """Retrieve the thread's sleep interval.

        Returns:
            int: The sleep interval (in seconds) for the thread.

        Note:
            The method will look for an enviroment variable (SLEEP_INTERVAL).
            If the environment variable isn't set or cannot be parsed as an integer,
            the method returns the default interval of 30 seconds.

        """

        return self.app_config.SLEEP_INTERVAL

    def data_resource_exists(self, data_resource_name):
        """ Checks if a data resource already exists.

        Returns:
            (bool): True if the data resource exists. False if not.

        """

        exists = False
        for data_resource in self.data_resources:
            if data_resource.data_resource_name.lower() == data_resource_name.lower():
                exists = True
                break
        return exists

    def data_resource_changed(self, data_resource_name, checksum):
        changed = False
        for data_resource in self.data_resources:
            if data_resource.data_resource_name.lower() == data_resource_name.lower():
                if data_resource.checksum != checksum:
                    return True
                else:
                    break
        return False

    def get_data_resource_index(self, data_resource_name):
        index = -1
        for idx, data_resource in enumerate(self.data_resources):
            if data_resource.data_resource_name.lower() == data_resource_name.lower():
                index = idx
                break
        print('index is {}'.format(index))
        return index

    def monitor_data_resources(self):
        """Monitor data resources.

        Note:
            This method is responsible for checking for new data resources and determining
            changes to existing ones. It does have a relatively high degree of overhead in
            that it queries the filesystem quite frequently; however, it tries to limit the
            impact by running in a thread that is logically separated from the main
            application.

        """
        schema_dir = self.get_data_resource_schema_path()
        if os.path.exists(schema_dir) and os.path.isdir(schema_dir):
            schemas = os.listdir(schema_dir)
            for schema in schemas:
                with open(os.path.join(self.get_data_resource_schema_path(), schema), 'r') as fh:
                    schema_obj = json.load(fh)
                try:
                    checksum = hashlib.md5(json.dumps(
                        schema_obj, sort_keys=True).encode('utf-8')).hexdigest()
                    data_resource_name = schema_obj['api']['resource']
                    api_schema = schema_obj['api']['methods']
                    table_name = schema_obj['datastore']['tablename']
                    table_schema = schema_obj['datastore']['schema']
                    if self.data_resource_exists(data_resource_name):
                        if self.data_resource_changed(data_resource_name, checksum):
                            index = self.get_data_resource_index(
                                data_resource_name)
                            if index > -1:
                                self.data_resources[index].datastore_object = self.data_model_factory.create_table_from_dict(
                                    self.data_resources[index].table_schema, self.data_resources[index].table_name)
                                print(self.data_resources[index])
                                print('Data Resource Changed')
                        else:
                            print('Data Resource Same')
                    else:
                        new_resource = DataResource()
                        new_resource.checksum = checksum
                        new_resource.data_resource_name = data_resource_name
                        new_resource.api_methods = api_schema
                        new_resource.table_name = table_name
                        new_resource.table_schema = table_schema
                        new_resource.datastore_object = self.data_model_factory.create_table_from_dict(
                            new_resource.table_schema, new_resource.table_name)
                        new_resource.api_object = self.api_factory.create_api_from_dict(
                            api_schema, data_resource_name, table_name, self.api, new_resource.datastore_object)
                        self.data_resources.append(new_resource)
                except KeyError:
                    print('Error in schema...')
        else:
            print('Schema directory does not exist')

    def run(self):
        """Run the data resource manager."""
        self.data_model_factory.upgrade()
        self.data_model_factory.create_checksum_table()
        self.data_model_factory.create_log_table()
        while True:
            print('Data Resource Monitor Running...')
            self.monitor_data_resources()
            print('Data Resource Monitor Sleeping for {} seconds...'.format(
                self.get_sleep_interval()))
            sleep(self.get_sleep_interval())

    def create_app(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_resource(self.available_services,
                              '/', endpoint='all_services_ep')
        return self.app
