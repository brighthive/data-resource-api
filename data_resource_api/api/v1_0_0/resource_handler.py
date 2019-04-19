"""Generic Resource Handler.

"""


class ResourceHandler(object):
    def get_all(self, data_resource):
        return {'message': 'get all'}, 200

    def insert_one(self, data_resource):
        return {'message': 'inserted one'}, 200

    def get_one(self, id, data_resource):
        return {'message': 'get one {}'.format(id)}, 200

    def update_one(self, id, data_resource):
        pass

    def delete_one(self, id, data_resource):
        pass
