"""
This should encapsulate all of the http services
for the DR API test code.
"""
from expects import expect, be_an, raise_error, have_property, equal, be_empty
import json

JSON_ROUTE = '/json'


class ApiHelper:
    @staticmethod
    def post_a_json(client, json_dict: dict):
        route = JSON_ROUTE
        post_body = {
            "json": dict(json_dict)
        }
        response = client.post(route, json=post_body)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(201))
        return body['id']

    @staticmethod
    def get_a_json_by_id(client, id: int):
        route = JSON_ROUTE
        response = client.get(f'{route}/{id}')
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        return body
