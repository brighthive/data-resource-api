from rest_operations import _get_one, _post_one, _get_many


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

    def _authorized(self):
        pass

    def base(self, verb: str, fns: dict, api_schema: dict, error_fn: function):
        error_fn()
        if self._authorized:
            return fns['secure_method']
        else:
            return fns['unsecure_method']

    def _error_if_disabled(self):
        raise NotImplementedError


class VersionedResourceMany(VersionedResourceParent):
    def _error_if_disabled(verb, resource, api_schema):
        # do something
        return self._error_if_disabled(verb, api_schema)

    def get_many(self):
        fns = {
            'secure_method': _get_one_secure,
            'unsecure_method': _get_one
        }

        self.base('get_many', fns, self.api_schema)


class VersionedResource(VersionedResourceParent):
    def get_one(self):
        fns = {
            'secure_method': _get_one_secure,
            'unsecure_method': _get_one
        }

        self.base('get', fns, self.api_schema)

    def post_one(self):
        fns = {
            'secure_method': _post_one_secure,
            'unsecure_method': _post_one
        }

        self.base('get', fns, self.api_schema)

    def patch_one(self):
        pass

    def put_one(self):
        pass

    def delete_one(self):
        pass