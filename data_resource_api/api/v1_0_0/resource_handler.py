"""Generic Resource Handler.

"""

import json
from data_resource_api.db import Session


class ResourceHandler(object):
    def build_json_from_object(self, obj: object):
        resp = {key: value for key, value in obj.__dict__.items(
        ) if not key.startswith('_') and not callable(key)}
        return resp

    def get_all(self, data_resource):
        session = Session()
        response = []
        try:
            results = session.query(data_resource).all()
            for row in results:
                response.append(self.build_json_from_object(row))
        except Exception:
            print('exception to be logged')
        return response, 200
        session.close()

    def insert_one(self, data_resource):
        return {'message': 'inserted one'}, 200

    def get_one(self, id, data_resource):
        return {'message': 'get one {}'.format(id)}, 200

    def update_one(self, id, data_resource):
        pass

    def delete_one(self, id, data_resource):
        pass
