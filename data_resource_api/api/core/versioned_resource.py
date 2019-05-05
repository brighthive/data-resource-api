"""Versioned Resource

This class extends the Flask Restful Resource class with the ability to look for
the API version number in the request header.

"""

from flask_restful import Resource
from flask import request
from data_resource_api.api.v1_0_0 import ResourceHandler as V1_0_0_ResourceHandler


class VersionedResource(Resource):
    __slots__ = ['data_resource_name',
                 'data_model', 'table_schema', 'api_schema']

    def __init__(self):
        Resource.__init__(self)

    def get_api_version(self, headers):
        try:
            api_version = headers['X-Api-Version']
        except Exception:
            api_version = '1.0.0'
        return api_version

    def get_resource_handler(self, headers):
        if self.get_api_version(headers) == '1.0.0':
            return V1_0_0_ResourceHandler()
        else:
            return V1_0_0_ResourceHandler()

    def get(self, id=None):
        if self.api_schema['get']['enabled']:
            offset = 0
            limit = 20
            try:
                offset = request.args['offset']
            except Exception:
                pass

            try:
                limit = request.args['limit']
            except Exception:
                pass

            if id is None:
                if self.api_schema['get']['secured']:
                    return self.get_resource_handler(request.headers).get_all_secure(self.data_model, self.data_resource_name, offset, limit)
                else:
                    return self.get_resource_handler(request.headers).get_all(self.data_model, self.data_resource_name, offset, limit)
            else:
                if self.api_schema['get']['secured']:
                    return self.get_resource_handler(request.headers).get_one_secure(id, self.data_model, self.data_resource_name, self.table_schema)
                else:
                    return self.get_resource_handler(request.headers).get_one(id, self.data_model, self.data_resource_name, self.table_schema)
        else:
            return {'error': 'Method not allowed.'}, 405

    def post(self):
        if self.api_schema['post']['enabled']:
            if self.api_schema['post']['secured']:
                return self.get_resource_handler(request.headers).insert_one_secure(self.data_model, self.data_resource_name, self.table_schema, request)
            else:
                return self.get_resource_handler(request.headers).insert_one(self.data_model, self.data_resource_name, self.table_schema, request)
        else:
            return {'error': 'Method not allowed.'}, 405

    def put(self, id):
        if self.api_schema['put']['enabled']:
            if self.api_schema['put']['secured']:
                return {'message': 'put secured'}
            else:
                return {'message': 'put'}
        else:
            return {'error': 'Method not allowed.'}, 405

    def patch(self, id):
        if self.api_schema['patch']['enabled']:
            if self.api_schema['patch']['secured']:
                return {'message': 'patch secure'}
            else:
                return {'message': 'patch'}
        else:
            return {'error': 'Method not allowed.'}, 405

    def delete(self, id):
        if self.api_schema['delete']['enabled']:
            if self.api_schema['delete']['secured']:
                return {'message': 'delete secure'}
            else:
                return {'message': 'delete'}
        else:
            return {'error': 'Method not allowed.'}, 405
