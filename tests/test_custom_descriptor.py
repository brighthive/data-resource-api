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

        expect(response.status_code).to(equal(201))

        return body['id']

    @staticmethod
    def get_a_framework_by_id(c, id: int):
        route = '/frameworks'
        response = c.get(f'{route}/{id}')
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))

        return body

    @staticmethod
    def post_a_framework_with_no_skills(c):
        route = '/frameworks'
        post_body = {
            "name": "test framework"
        }
        response = c.post(route, json=post_body)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(201))

        return body['id']

    @staticmethod
    def post_json(c, data: object):
        route = '/frameworks'
        post_body = {
            "name": "test",
            "jsonb": data
        }
        response = c.post(route, json=post_body)
        body = json.loads(response.data)

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

        expect(response.status_code).to(equal(200))

    @staticmethod
    def patch_a_framework_skill(c, framework_id: int, skills_list: list):
        route = f'/frameworks/{framework_id}/skills'
        patch_body = {
            "skills": skills_list
        }
        response = c.patch(route, json=patch_body)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))

    @staticmethod
    def check_for_skills_on_framework(c, framework_id: int, skills_list: list):
        route = f'/frameworks/{framework_id}/skills'
        response = c.get(route)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        expect(body['skills']).to(equal(skills_list))

    @staticmethod
    def get_frameworks_on_skill(c, skill_id: int):
        route = f'/skills/{skill_id}/frameworks'
        response = c.get(route)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        return body

    @staticmethod
    def delete_a_framework_skill(c, framework_id: int, skills_list: list):
        route = f'/frameworks/{framework_id}/skills'
        delete_body = {
            'skills': skills_list
        }

        response = c.delete(route, json=delete_body)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))  # 204
        return body


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
        ApiHelper.check_for_skills_on_framework(c, framework_id, [skill_3])

    def test_mn_patch(self, frameworks_skills_client):
        c = frameworks_skills_client

        skill_1 = ApiHelper.post_a_skill(c, "skill1")
        skill_2 = ApiHelper.post_a_skill(c, "skill2")
        skills_list = [skill_1, skill_2]
        skill_3 = ApiHelper.post_a_skill(c, "skill3")

        framework_id = ApiHelper.post_a_framework(c, skills_list)
        ApiHelper.patch_a_framework_skill(c, framework_id, [skill_3])
        ApiHelper.check_for_skills_on_framework(c, framework_id, [skill_1, skill_2, skill_3])

    def test_mn_delete_one(self, frameworks_skills_client):
        c = frameworks_skills_client

        skill_1 = ApiHelper.post_a_skill(c, "skill1")
        skill_2 = ApiHelper.post_a_skill(c, "skill2")
        skills_list = [skill_1, skill_2]

        framework_id = ApiHelper.post_a_framework(c, skills_list)
        resp = ApiHelper.delete_a_framework_skill(c, framework_id, [skill_1])

        expect(resp['skills']).to(equal([skill_2]))

    def test_mn_delete_many(self, frameworks_skills_client):
        c = frameworks_skills_client

        skill_1 = ApiHelper.post_a_skill(c, "skill1")
        skill_2 = ApiHelper.post_a_skill(c, "skill2")
        skill_3 = ApiHelper.post_a_skill(c, "skill3")
        skills_list = [skill_1, skill_2, skill_3]
        framework_id = ApiHelper.post_a_framework(c, skills_list)

        resp = ApiHelper.delete_a_framework_skill(c, framework_id, [skill_1, skill_3])

        expect(resp['skills']).to(equal([skill_2]))

    def test_mn_delete_relationship_that_does_not_exist(self, frameworks_skills_client):
        c = frameworks_skills_client

        skill_1 = ApiHelper.post_a_skill(c, "skill1")
        skill_2 = ApiHelper.post_a_skill(c, "skill2")
        skill_3 = ApiHelper.post_a_skill(c, "skill3")
        skills_list = [skill_1, skill_2]
        framework_id = ApiHelper.post_a_framework(c, skills_list)

        resp = ApiHelper.delete_a_framework_skill(c, framework_id, [skill_3])

        expect(resp['skills']).to(equal([skill_1, skill_2]))

    def test_mn_reverse_relationship(self, frameworks_skills_client):
        c = frameworks_skills_client

        skill_1 = ApiHelper.post_a_skill(c, "skill1")
        framework_id = ApiHelper.post_a_framework(c, [skill_1])

        resp = ApiHelper.get_frameworks_on_skill(c, skill_1)

        expect(resp['frameworks']).to(equal([framework_id]))

    def test_json(self, frameworks_skills_client):
        c = frameworks_skills_client

        json_framework_id = ApiHelper.post_json(c, {"testkey": "testvalue"})

        resp = ApiHelper.get_a_framework_by_id(c, json_framework_id)

        expect(resp['jsonb']).to(equal("{'testkey': 'testvalue'}"))
