from expects import expect, be_an, raise_error, have_property, equal, be_empty
from data_resource_api import ConfigurationFactory, InvalidConfigurationError
import json


class TestStartup(object):
    def test_load_descriptor(self, frameworks_skills_client):
        ## Get
        def get_all_frameworks():
            route = '/frameworks'
            response = frameworks_skills_client.get(route)
            body = json.loads(response.data)

            expect(response.status_code).to(equal(200))
            expect(body['frameworks']).to(be_empty)
        
        
        ## Put a framework
        def post_a_framework():
            route = '/frameworks'
            post_body = {
                "name": "test framework"
            }
            response = frameworks_skills_client.post(route, json=post_body)
            expect(response.status_code).to(equal(201))


        ## Check for one item
        def check_for_one_framework():
            route = '/frameworks'
            response = frameworks_skills_client.get(route)
            body = json.loads(response.data)

            expect(response.status_code).to(equal(200))
            expect(len(body['frameworks'])).to(equal(1))
        
        
        ## Get m:n
        def get_many_route():
            route = '/framework/1/skills'
            response = frameworks_skills_client.get(route)
            body = json.loads(response.data)

            expect(response.status_code).to(equal(200))
            print(body)
            expect(body['skills']).to(be_empty)


        ## Put skills on the framework
        def post_two_skills_to_framework():
            route = '/framework/1/skills'
            post_body = [
                {"skills_text": "skill 1"},
                {"skills_text": "skill 2"}
            ]
            response = frameworks_skills_client.post(route, json=post_body)
            expect(response.status_code).to(equal(201))
        

        # def post_one_skill_to_framework(): return

        ## Verify they are there
        def verify_skills_count():
            route = '/framework/1/skills'
            response = frameworks_skills_client.get(route)
            body = json.loads(response.data)

            expect(response.status_code).to(equal(200))
            expect(len(body['skills'])).to(equal(2))
        
        get_all_frameworks()
        post_a_framework()
        check_for_one_framework()
        get_many_route()
        post_two_skills_to_framework()
        verify_skills_count()