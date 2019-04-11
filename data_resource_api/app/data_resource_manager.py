"""Data Resource Manager

The Data Resource Manager manages the lifecycles of all data resources. It exists as a background process that
polls the filesystem for new data resource specifications and removes old ones. The Data Resource Manager is
also responsible for creating the Flask application that sits at the front of the data resource.


"""

import os
import json
from threading import Thread
from time import sleep
from flask import Flask
from flask_restful import Api, Resource
from data_resource_api.config import ConfigurationFactory
from data_resource_api.db import engine
from data_resource_api.app import DataResource


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

    def data_resource_changed(self, data_resource_name, api_methods, table_name, table_schema):
        changed = False
        for data_resource in self.data_resources:
            if data_resource.data_resource_name.lower() == data_resource_name.lower():
                if data_resource.api_methods != api_methods or data_resource.table_name != table_name or\
                        data_resource.table_schema != table_schema:
                    return True
        return False

    def monitor_data_resources(self):
        """Monitor data resources."""
        schema_dir = self.get_data_resource_schema_path()
        if os.path.exists(schema_dir) and os.path.isdir(schema_dir):
            schemas = os.listdir(schema_dir)
            for schema in schemas:
                with open(os.path.join(self.get_data_resource_schema_path(), schema), 'r') as fh:
                    schema_obj = json.load(fh)

                # build a schema
                try:
                    data_resource_name = schema_obj['api']['resource']
                    api_methods = schema_obj['api']['methods']
                    table_name = schema_obj['datastore']['tablename']
                    table_schema = schema_obj['datastore']['schema']
                    if self.data_resource_exists(data_resource_name):
                        if self.data_resource_changed(data_resource_name, api_methods, table_name, table_schema):
                            print('resource changed...')
                        else:
                            print('resource unchanged')
                    else:
                        new_resource = DataResource()
                        new_resource.data_resource_name = data_resource_name
                        new_resource.api_methods = api_methods
                        new_resource.table_name = table_name
                        new_resource.table_schema = table_schema
                        self.data_resources.append(new_resource)
                except Exception as e:
                    print(
                        'Error Parsing Schema `{}` Failed With Exception `{}`'.format(schema, e))

        else:
            print('Schema directory does not exist')

    def run(self):
        """Run the data resource manager."""

        while True:
            self.monitor_data_resources()
            sleep(self.get_sleep_interval())

    def create_app(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_resource(Resource, '/', endpoint='placeholder_ep')
        return self.app
