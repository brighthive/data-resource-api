"""Versioned Resource

This class extends the Flask Restful Resource class with the ability to look for
the API version number in the request header.

"""

from flask_restful import Resource
from flask import request
from data_resource_api.api.v1_0_0 import ResourceHandler as V1_0_0_ResourceHandler
from data_resource_api.app.exception_handler import MethodNotAllowed


class VersionedResourceParent(Resource):
    __slots__ = ['data_resource_name',
                 'data_model', 'table_schema', 'api_schema', 'restricted_fields']

    def __init__(self):
        Resource.__init__(self)

    def get_api_version(self, headers):
        try:
            api_version = headers['X-Api-Version']
        except KeyError:
            api_version = '1.0.0'
        return api_version

    def get_resource_handler(self, headers):
        if self.get_api_version(headers) == '1.0.0':
            return V1_0_0_ResourceHandler()
        else:
            return V1_0_0_ResourceHandler()


class VersionedResourceMany(VersionedResourceParent):
    def get(self, id=None):
        # route should be parent/<id>/child
        paths = request.path.split('/')
        parent, child = paths[1], paths[3]
        return self.get_resource_handler(request.headers).get_many_one(id, parent, child)


class VersionedResource(VersionedResourceParent):
    def get(self, id=None):
        if self.api_schema['get']['enabled']:
            if request.path.endswith('/query'):
                raise MethodNotAllowed()
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
                    return self.get_resource_handler(request.headers).get_all_secure(self.data_model, self.data_resource_name, self.restricted_fields, offset, limit)
                else:
                    return self.get_resource_handler(request.headers).get_all(self.data_model, self.data_resource_name, self.restricted_fields, offset, limit)
            else:
                if self.api_schema['get']['secured']:
                    return self.get_resource_handler(request.headers).get_one_secure(id, self.data_model, self.data_resource_name, self.table_schema)
                else:
                    return self.get_resource_handler(request.headers).get_one(id, self.data_model, self.data_resource_name, self.table_schema)
        else:
            raise MethodNotAllowed()

    def post(self):
        if self.api_schema['post']['enabled']:
            if self.api_schema['post']['secured']:
                if request.path.endswith('/query'):
                    return self.get_resource_handler(request.headers).query_secure(self.data_model, self.data_resource_name, self.restricted_fields, self.table_schema, request)
                else:
                    return self.get_resource_handler(request.headers).insert_one_secure(self.data_model, self.data_resource_name, self.table_schema, request)
            else:
                if request.path.endswith('/query'):
                    return self.get_resource_handler(request.headers).query(self.data_model, self.data_resource_name, self.restricted_fields, self.table_schema, request)
                else:
                    return self.get_resource_handler(request.headers).insert_one(self.data_model, self.data_resource_name, self.table_schema, request)
        else:
            raise MethodNotAllowed()

    def put(self, id):
        if self.api_schema['put']['enabled']:
            if request.path.endswith('/query'):
                raise MethodNotAllowed()
            if self.api_schema['put']['secured']:
                return self.get_resource_handler(request.headers).update_one_secure(id, self.data_model, self.data_resource_name, self.table_schema, self.restricted_fields, request, mode='PUT')
            else:
                return self.get_resource_handler(request.headers).update_one(id, self.data_model, self.data_resource_name, self.table_schema, self.restricted_fields, request, mode='PUT')
        else:
            raise MethodNotAllowed()

    def patch(self, id):
        if self.api_schema['patch']['enabled']:
            if request.path.endswith('/query'):
                raise MethodNotAllowed()
            if self.api_schema['patch']['secured']:
                return self.get_resource_handler(request.headers).update_one_secure(id, self.data_model, self.data_resource_name, self.table_schema, self.restricted_fields, request, mode='PATCH')
            else:
                return self.get_resource_handler(request.headers).update_one_secure(id, self.data_model, self.data_resource_name, self.table_schema, self.restricted_fields, request, mode='PATCH')
        else:
            raise MethodNotAllowed()

    def delete(self, id):
        if self.api_schema['delete']['enabled']:
            if request.path.endswith('/query'):
                raise MethodNotAllowed()
            if self.api_schema['delete']['secured']:
                return {'message': 'delete secure'}
            else:
                return {'message': 'delete'}
        else:
            raise MethodNotAllowed()
