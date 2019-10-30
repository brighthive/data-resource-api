from expects import expect, be_an, raise_error, have_property, equal, be_empty
from data_resource_api import ConfigurationFactory, InvalidConfigurationError
import json


class TestStartup(object):
    def test_load_descriptor(self, frameworks_skills_client):
        def get_all_frameworks():
            route = '/frameworks'
            response = frameworks_skills_client.get(route)
            body = json.loads(response.data)

            expect(response.status_code).to(equal(200))
            expect(body['frameworks']).to(be_empty)

        def post_a_skill(skill_text: str):
            route = '/skills'
            post_body = {
                "text": skill_text
            }
            response = frameworks_skills_client.post(route, json=post_body)
            expect(response.status_code).to(equal(201))

        def post_a_framework(skills: list):
            route = '/frameworks'
            post_body = {
                "name": "test framework",
                "skills": skills
            }
            response = frameworks_skills_client.post(route, json=post_body)
            body = json.loads(response.data)

            print(body)
            expect(response.status_code).to(equal(201))

        def check_for_skills_on_framework():
            route = '/frameworks/1/skills'
            response = frameworks_skills_client.get(route)
            body = json.loads(response.data)

            print(body)
            expect(response.status_code).to(equal(200))
            expect(body['skills']).to(equal([1, 2]))

        get_all_frameworks()
        post_a_skill("skill1")
        post_a_skill("skill2")
        post_a_framework([1, 2])
        check_for_skills_on_framework()

    def test_relationships(self, frameworks_skills_client):
        def post_a_framework():
            route = '/frameworks'
            post_body = {
                "name": "test framework"
            }
            response = frameworks_skills_client.post(route, json=post_body)
            body = json.loads(response.data)

            expect(response.status_code).to(equal(201))
            return body['id']

        def get_wrong_relationship(framework_id: int):
            route = f'/frameworks/{framework_id}/providers'
            response = frameworks_skills_client.get(route)
            body = json.loads(response.data)

            expect(response.status_code).to(equal(200))  # should be 404

            error_message = "exception is 404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
            expect(body['error']).to(equal(error_message))

        def get_nonexistant_relationship(framework_id: int):
            route = f'/frameworks/{framework_id}/skills'
            response = frameworks_skills_client.get(route)

            body = json.loads(response.data)

            expect(response.status_code).to(equal(200))
            expect(len(body['skills'])).to(equal(0))

        framework_id = post_a_framework()
        get_wrong_relationship(framework_id)
        get_nonexistant_relationship(framework_id)