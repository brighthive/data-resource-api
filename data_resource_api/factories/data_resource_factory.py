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
            api (object): Flaskrestful api object
            table_obj (object): sqlalchemy.ext.declarative.api.DeclarativeMeta
            table_schema (dict): from descriptor
            restricted_fields (list): Fields that should not be queryable

        """
        new_api = None
        resources = [f'/{endpoint_name}',
                     f'/{endpoint_name}/<id>',
                     f'/{endpoint_name}/query']

        ## If we have a many to many
            ## resources.append(f'/{endpoint_name}/<id>/{child_name}')
        print("!!!!!!!!!!create API many-to-many resources!!!!!!!!!!!")
        if 'custom' in api_schema:
            for custom_resource in api_schema['custom']:
                custom_table = custom_resource['resource'].split('/')
                print(custom_table)
                many_endpoint = f'/{custom_table[1]}/<id>/{custom_table[2]}'
                print(many_endpoint)
                "framework/<id>/skills -> framework(1).skills"
                resources.append(many_endpoint)
        print("!!!!!!!!!end!!!!!!!!!!!!")

        new_api = type(
            endpoint_name,
            (VersionedResource,),
            {
                'data_resource_name': table_name,
                'data_model': table_obj,
                'table_schema': table_schema,
                'api_schema': api_schema,
                'restricted_fields': restricted_fields
            })

        for idx, resource in enumerate(resources):
            api.add_resource(
                new_api,
                resource,
                endpoint=f'{endpoint_name}_ep_{idx}'
            )
        print("################")
        print(vars(new_api))
        print(vars(api))
        return new_api
