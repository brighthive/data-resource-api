import json

from tests.service import ApiHelper

import pytest
from expects import be_an, be_empty, equal, expect, have_property, raise_error


@pytest.mark.requiresdb
def test_load_descriptor(frameworks_skills_client):
    c = frameworks_skills_client
    skill_1 = ApiHelper.post_a_skill(c, "skill1")
    skill_2 = ApiHelper.post_a_skill(c, "skill2")
    skills_list = [skill_1, skill_2]
    framework_id = ApiHelper.post_a_framework(c, skills_list)

    ApiHelper.check_for_skills_on_framework(c, framework_id, skills_list)


@pytest.mark.requiresdb
def test_relationships(frameworks_skills_client):
    c = frameworks_skills_client

    def get_wrong_relationship(framework_id: int):
        route = f"/frameworks/{framework_id}/providers"
        response = frameworks_skills_client.get(route)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(404))

        error_message = "Location not found"
        expect(body["error"]).to(equal(error_message))

    def get_nonexistant_relationship(framework_id: int):
        route = f"/frameworks/{framework_id}/skills"
        response = frameworks_skills_client.get(route)

        body = json.loads(response.data)
        print(body)

        expect(response.status_code).to(equal(200))
        expect(len(body["skills"])).to(equal(0))

    framework_id = ApiHelper.post_a_framework_with_no_skills(c)
    get_wrong_relationship(framework_id)
    get_nonexistant_relationship(framework_id)


@pytest.mark.requiresdb
def test_mn_put(frameworks_skills_client):
    c = frameworks_skills_client

    skill_1 = ApiHelper.post_a_skill(c, "skill1")
    skill_2 = ApiHelper.post_a_skill(c, "skill2")
    skills_list = [skill_1, skill_2]
    skill_3 = ApiHelper.post_a_skill(c, "skill3")
    framework_id = ApiHelper.post_a_framework(c, skills_list)

    ApiHelper.put_a_framework_skill(c, framework_id, [skill_3])
    ApiHelper.check_for_skills_on_framework(c, framework_id, [skill_3])


@pytest.mark.requiresdb
def test_mn_patch(frameworks_skills_client):
    c = frameworks_skills_client

    skill_1 = ApiHelper.post_a_skill(c, "skill1")
    skill_2 = ApiHelper.post_a_skill(c, "skill2")
    skills_list = [skill_1, skill_2]
    skill_3 = ApiHelper.post_a_skill(c, "skill3")

    framework_id = ApiHelper.post_a_framework(c, skills_list)
    ApiHelper.patch_a_framework_skill(c, framework_id, [skill_3])
    ApiHelper.check_for_skills_on_framework(
        c, framework_id, [skill_1, skill_2, skill_3]
    )


@pytest.mark.requiresdb
def test_mn_delete_one(frameworks_skills_client):
    c = frameworks_skills_client

    skill_1 = ApiHelper.post_a_skill(c, "skill1")
    skill_2 = ApiHelper.post_a_skill(c, "skill2")
    skills_list = [skill_1, skill_2]

    framework_id = ApiHelper.post_a_framework(c, skills_list)
    resp = ApiHelper.delete_a_framework_skill(c, framework_id, [skill_1])

    expect(resp["skills"]).to(equal([skill_2]))


@pytest.mark.requiresdb
def test_mn_delete_many(frameworks_skills_client):
    c = frameworks_skills_client

    skill_1 = ApiHelper.post_a_skill(c, "skill1")
    skill_2 = ApiHelper.post_a_skill(c, "skill2")
    skill_3 = ApiHelper.post_a_skill(c, "skill3")
    skills_list = [skill_1, skill_2, skill_3]
    framework_id = ApiHelper.post_a_framework(c, skills_list)

    resp = ApiHelper.delete_a_framework_skill(c, framework_id, [skill_1, skill_3])

    expect(resp["skills"]).to(equal([skill_2]))


@pytest.mark.requiresdb
def test_mn_delete_relationship_that_does_not_exist(frameworks_skills_client):
    c = frameworks_skills_client

    skill_1 = ApiHelper.post_a_skill(c, "skill1")
    skill_2 = ApiHelper.post_a_skill(c, "skill2")
    skill_3 = ApiHelper.post_a_skill(c, "skill3")
    skills_list = [skill_1, skill_2]
    framework_id = ApiHelper.post_a_framework(c, skills_list)

    resp = ApiHelper.delete_a_framework_skill(c, framework_id, [skill_3])

    expect(resp["skills"]).to(equal([skill_1, skill_2]))


@pytest.mark.requiresdb
def test_mn_reverse_relationship(frameworks_skills_client):
    c = frameworks_skills_client

    skill_1 = ApiHelper.post_a_skill(c, "skill1")
    framework_id = ApiHelper.post_a_framework(c, [skill_1])

    resp = ApiHelper.get_frameworks_on_skill(c, skill_1)

    expect(resp["frameworks"]).to(equal([framework_id]))
