"""
This should encapsulate all of the http services
for the DR API test code.
"""
from expects import expect, be_an, raise_error, have_property, equal, be_empty
import json

JSON_ROUTE = '/json'
SKILLS_ROUTE = '/skills'
FRAMEWORKS_ROUTE = '/frameworks'
MANY_TO_MANY_ROUTE = '{parent}/{parent_id}/{child}'


def MN_FRAMEWORKS_SKILLS_ROUTE(parent_id):
    return MANY_TO_MANY_ROUTE.format(
        parent=FRAMEWORKS_ROUTE.replace("/", ""),
        parent_id=parent_id,
        child=SKILLS_ROUTE.replace("/", ""))


def MN_SKILLS_FRAMEWORK_ROUTE(parent_id):
    return MANY_TO_MANY_ROUTE.format(
        parent=SKILLS_ROUTE.replace("/", ""),
        parent_id=parent_id,
        child=FRAMEWORKS_ROUTE.replace("/", ""))


class ApiHelper:
    # test_json_descriptor
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

    # test_many_to_many_descriptor
    @staticmethod
    def post_a_skill(c, skill_text: str):
        route = SKILLS_ROUTE
        post_body = {
            "text": skill_text
        }
        response = c.post(route, json=post_body)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(201))
        return body['id']

    @staticmethod
    def post_a_framework(c, skills: list):
        route = FRAMEWORKS_ROUTE
        post_body = {
            "name": "test framework",
            "skills": skills
        }
        response = c.post(route, json=post_body)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(201))

        return body['id']

    @staticmethod
    def get_a_framework_by_id(c, id: int):
        route = FRAMEWORKS_ROUTE
        response = c.get(f'{route}/{id}')
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))

        return body

    @staticmethod
    def post_a_framework_with_no_skills(c):
        route = FRAMEWORKS_ROUTE
        post_body = {
            "name": "test framework"
        }
        response = c.post(route, json=post_body)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(201))

        return body['id']

    @staticmethod
    def put_a_framework_skill(c, framework_id: int, skills: list):
        route = MN_FRAMEWORKS_SKILLS_ROUTE(framework_id)
        put_body = {
            "skills": skills
        }
        response = c.put(route, json=put_body)
        _ = json.loads(response.data)

        expect(response.status_code).to(equal(200))

    @staticmethod
    def patch_a_framework_skill(c, framework_id: int, skills_list: list):
        route = MN_FRAMEWORKS_SKILLS_ROUTE(framework_id)
        patch_body = {
            "skills": skills_list
        }
        response = c.patch(route, json=patch_body)
        _ = json.loads(response.data)

        expect(response.status_code).to(equal(200))

    @staticmethod
    def check_for_skills_on_framework(c, framework_id: int, skills_list: list):
        route = MN_FRAMEWORKS_SKILLS_ROUTE(framework_id)
        response = c.get(route)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        expect(body['skills']).to(equal(skills_list))

    @staticmethod
    def get_frameworks_on_skill(c, skill_id: int):
        route = MN_SKILLS_FRAMEWORK_ROUTE(skill_id)
        response = c.get(route)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        return body

    @staticmethod
    def delete_a_framework_skill(c, framework_id: int, skills_list: list):
        route = MN_FRAMEWORKS_SKILLS_ROUTE(framework_id)
        delete_body = {
            'skills': skills_list
        }

        response = c.delete(route, json=delete_body)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))  # 204
        return body