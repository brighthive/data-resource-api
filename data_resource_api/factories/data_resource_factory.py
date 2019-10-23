"""Data Resource Factory

This module contains a factory object for creating API resources.

"""

import hashlib
import json
from data_resource_api.config import ConfigurationFactory
from data_resource_api.api import VersionedResource


class DataResourceFactory(object):
    """API factory for generating new Flask resources.

    """

    def get_app_config(self):
        """Convenience method for returning application configuration.

        Returns:
            Config: Configuration object based on the current application environment.

        """
        return ConfigurationFactory.from_env()

    def create_api_from_dict(self, api_schema: dict, endpoint_name: str, table_name: str, api: object, table_obj: object, table_schema: dict, restricted_fields: list = []):
        """Create an API endpoint from a custom specification.

        Args:
            api_schema (dict): API schema as a dict.
            endpoint_name (str): Name of the endpoint.
            table_name (str): Name of the data model (i.e. table) associated with the endpoint.

        """
        new_api = None
        resources = ['/{}'.format(endpoint_name),
                     '/{}/<id>'.format(endpoint_name),
                     '/{}/query'.format(endpoint_name)]

        if 'custom' in api_schema:
            for custom_resource in api_schema['custom']:
                custom_table = custom_resource['resource'].split('/')
                resources.append(f'/{custom_table[1]}/<id>/{custom_table[2]}')
                resources.append(
                    f'/{custom_table[1]}/<id>/{custom_table[2]}/<child_id>'
                ) # DELETE route

        new_api = type(endpoint_name, (VersionedResource,),
                       {'data_resource_name': table_name,
                        'data_model': table_obj,
                        'table_schema': table_schema,
                        'api_schema': api_schema,
                        'restricted_fields': restricted_fields})

        for idx, resource in enumerate(resources):
            api.add_resource(
                new_api,
                resource,
                endpoint=f'{endpoint_name}_ep_{idx}'
            )
        return new_api
