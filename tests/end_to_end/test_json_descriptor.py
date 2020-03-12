from expects import expect, be_an, raise_error, have_property, equal, be_empty
import json


class ApiHelper:
    @staticmethod
    def post_a_json(c, json_dict: dict):
        route = '/json'
        post_body = {
            "json": dict(json_dict)
        }
        response = c.post(route, json=post_body)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(201))
        return body['id']

    @staticmethod
    def get_a_json_by_id(c, id: int):
        route = '/json'
        response = c.get(f'{route}/{id}')
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))

        return body


def test_json_posts_and_returns_correctly(json_client):
    c = json_client

    json_body = {
        "test": 1234,
        "obj": {
            "key": "value"
        }
    }

    json_id = ApiHelper.post_a_json(c, json_body)

    resp = ApiHelper.get_a_json_by_id(c, json_id)

    expect(json.dumps(resp['json'], sort_keys=True)).to(equal(json.dumps(json_body, sort_keys=True)))


def test_nested_str_in_json_posts_and_returns_correctly(json_client):
    c = json_client

    json_body = {
        "test": 1234,
        "obj": "{\"key\": \"value\"\}"
    }

    json_id = ApiHelper.post_a_json(c, json_body)

    resp = ApiHelper.get_a_json_by_id(c, json_id)

    expect(json.dumps(resp['json'], sort_keys=True)).to(equal(json.dumps(json_body, sort_keys=True)))


def test_nested_nested_str_in_json_posts_and_returns_correctly(json_client):
    c = json_client

    json_body = {
        "test": 1234,
        "obj": {
            "but what about this": "{\"key\": \"value\"\}"
        }
    }

    json_id = ApiHelper.post_a_json(c, json_body)

    resp = ApiHelper.get_a_json_by_id(c, json_id)

    expect(json.dumps(resp['json'], sort_keys=True)).to(equal(json.dumps(json_body, sort_keys=True)))