from expects import expect, be_an, raise_error, have_property, equal, be_empty
import json
from tests.service import ApiHelper


class TestStartup():
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
        ApiHelper.check_for_skills_on_framework(
            c, framework_id, [skill_1, skill_2, skill_3])

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

        resp = ApiHelper.delete_a_framework_skill(
            c, framework_id, [skill_1, skill_3])

        expect(resp['skills']).to(equal([skill_2]))

    def test_mn_delete_relationship_that_does_not_exist(
            self, frameworks_skills_client):
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
