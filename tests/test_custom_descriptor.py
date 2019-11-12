from expects import expect, be_an, raise_error, have_property, equal, be_empty
from data_resource_api import ConfigurationFactory, InvalidConfigurationError
import json


class ApiHelper:
    @staticmethod
    def post_a_skill(c, skill_text: str):
        route = '/skills'
        post_body = {
            "text": skill_text
        }
        response = c.post(route, json=post_body)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(201))
        return body['id']

    @staticmethod
    def post_a_framework(c, skills: list):
        route = '/frameworks'
        post_body = {
            "name": "test framework",
            "skills": skills
        }
        response = c.post(route, json=post_body)
        body = json.loads(response.data)

        print(body)
        expect(response.status_code).to(equal(201))

        return body['id']

    @staticmethod
    def post_a_framework_with_no_skills(c):
        route = '/frameworks'
        post_body = {
            "name": "test framework"
        }
        response = c.post(route, json=post_body)
        body = json.loads(response.data)

        print(body)
        expect(response.status_code).to(equal(201))

        return body['id']

    @staticmethod
    def put_a_framework_skill(c, framework_id: int, skills: list):
        route = f'/frameworks/{framework_id}/skills'
        put_body = {
            "skills": skills
        }
        response = c.put(route, json=put_body)
        body = json.loads(response.data)

        print(body)
        expect(response.status_code).to(equal(201))

        return body['id']

    @staticmethod
    def check_for_skills_on_framework(c, framework_id, skills_list):
        route = f'/frameworks/{framework_id}/skills'
        response = c.get(route)
        body = json.loads(response.data)

        print(body)
        expect(response.status_code).to(equal(200))
        expect(body['skills']).to(equal(skills_list))


class TestStartup(object):
    def test_load_descriptor(self, frameworks_skills_client):
        c = frameworks_skills_client
        skill_1 = ApiHelper.post_a_skill(c, "skill1")
        skill_2 = ApiHelper.post_a_skill(c, "skill2")
        skills_list = [skill_1, skill_2]

        framework_id = ApiHelper.post_a_framework(c, skills_list)
        ApiHelper.check_for_skills_on_framework(c, framework_id, skills_list)

    def test_relationships(self, frameworks_skills_client):
        c = frameworks_skills_client

        def get_wrong_relationship(framework_id: int):
            route = f'/frameworks/{framework_id}/providers'
            response = frameworks_skills_client.get(route)
            body = json.loads(response.data)

            expect(response.status_code).to(equal(404))

            error_message = "Location not found"
            expect(body['error']).to(equal(error_message))

        def get_nonexistant_relationship(framework_id: int):
            route = f'/frameworks/{framework_id}/skills'
            response = frameworks_skills_client.get(route)

            body = json.loads(response.data)
            print(body)

            expect(response.status_code).to(equal(200))
            expect(len(body['skills'])).to(equal(0))

        framework_id = ApiHelper.post_a_framework_with_no_skills(c)
        get_wrong_relationship(framework_id)
        get_nonexistant_relationship(framework_id)

    def test_mn_put(self, frameworks_skills_client):
        c = frameworks_skills_client

        skill_1 = ApiHelper.post_a_skill(c, "skill1")
        skill_2 = ApiHelper.post_a_skill(c, "skill2")
        skills_list = [skill_1, skill_2]
        skill_3 = ApiHelper.post_a_skill(c, "skill3")

        framework_id = ApiHelper.post_a_framework(c, skills_list)
        ApiHelper.put_a_framework_skill(c, framework_id, [skill_3])
        ApiHelper.check_for_skills_on_framework(c, [skill_3])
