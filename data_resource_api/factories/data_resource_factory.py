"""Data Resource Factory

This module contains a factory object for creating API resources.

"""

import hashlib
import json
from data_resource_api.config import ConfigurationFactory
from data_resource_api.factories import DataModelFactory
from data_resource_api.api import VersionedResource


class DataResourceFactory(object):
    """API factory for generating new Flask resources.

    """

    def __init__(self):
        self.data_model_factory = DataModelFactory()

    def get_app_config(self):
        """Convenience method for returning application configuration.

        Returns:
            Config: Configuration object based on the current application environment.

        """
        return ConfigurationFactory.from_env()

    def create_api_from_dict(self, api_schema: dict, endpoint_name: str, table_name: str, api: object, table_obj: object):
        """Create an API endpoint from a custom specification.

        Args:
            api_schema (dict): API schema as a dict.
            endpoint_name (str): Name of the endpoint.
            table_name (str): Name of the data model (i.e. table) associated with the endpoint.

        """
        new_api = None
        checksum = self.data_model_factory.get_model_checksum(table_name)
        api_checksum = hashlib.md5(json.dumps(
            api_schema).encode('utf-8')).hexdigest()
        resources = ['/{}'.format(endpoint_name),
                     '/{}/<id>'.format(endpoint_name)]
        new_api = type(endpoint_name, (VersionedResource,),
                       {'data_resource_name': table_name,
                        'data_model': table_obj})
        for idx, resource in enumerate(resources):
            api.add_resource(new_api, resource,
                             endpoint='{}_ep_{}'.format(endpoint_name, idx))
        # for schema in api_schema:
        #     for key in schema.keys():
        #         if key.lower() == 'get':
        #             print('GET')
        #         elif key.lower() == 'post':
        #             print('POST')
        #         elif key.lower() == 'put':
        #             print('PUT')
        #         elif key.lower() == 'patch':
        #             print('PATCH')
        #         elif key.lower() == 'delete':
        #             print('DELETE')
        #         elif key.lower() == 'custom':
        #             print('CUSTOM')
        #             print(schema[key])
        return new_api
