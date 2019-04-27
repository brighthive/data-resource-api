"""Versioned Resource

This class extends the Flask Restful Resource class with the ability to look for
the API version number in the request header.

"""

from flask_restful import Resource
from flask import request
from data_resource_api.api.v1_0_0 import ResourceHandler as V1_0_0_ResourceHandler


class VersionedResource(Resource):
    __slots__ = ['data_resource']

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
        if id is None:
            return self.get_resource_handler(request.headers).get_all(self.data_resource)
        else:
            return self.get_resource_handler(request.headers).get_one(id, self.data_resource)

    def post(self):
        return {'message': 'posted!'}

    def put(self):
        return {'message': 'put'}

    def patch(self):
        return {'message': 'patch'}

    def delete(self):
        return {'message': 'delete'}
