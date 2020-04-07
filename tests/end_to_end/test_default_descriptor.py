import json

from tests.service import ApiHelper

import pytest
from expects import be_an, be_empty, equal, expect, have_property, raise_error


@pytest.mark.requiresdb
def test_get_post_put_patch_on_one_item(regular_client):
    # Get
    body = ApiHelper.get_credential(regular_client)
    expect(body["credentials"]).to(be_empty)
    expect(body["links"]).to(be_empty)

    # Post
    post_body = {"credential_name": "testtesttest"}
    credential_id = ApiHelper.post_a_credential(regular_client, post_body)

    body = ApiHelper.get_credential(regular_client)
    expect(len(body["credentials"])).to(equal(1))

    body = ApiHelper.get_credential(regular_client, credential_id)
    expect(body["credential_name"]).to(equal("testtesttest"))

    # Put
    put_body = {"credential_name": "asdf"}
    ApiHelper.put_a_credential(regular_client, put_body, credential_id)
    body = ApiHelper.get_credential(regular_client, credential_id)

    expect(body["credential_name"]).to(equal("asdf"))

    # Patch
    patch_body = {"credential_name": "qwery"}
    ApiHelper.patch_a_credential(regular_client, patch_body, credential_id)
    body = ApiHelper.get_credential(regular_client, credential_id)

    expect(body["credential_name"]).to(equal("qwery"))


@pytest.mark.requiresdb
def test_error_on_nonexistant_field(regular_client):
    post_body = {
        "credential_name": "test credential",
        "doesnotexist": "doesnotexist data",
    }
    ApiHelper.post_a_credential(regular_client, post_body, 400)


@pytest.mark.requiresdb
def test_programs(regular_client):
    _ = ApiHelper.get_program(regular_client)
    # expect(body['message']).to(equal('Access Denied'))


@pytest.mark.requiresdb
def test_pagination(regular_client):
    post_body = {"credential_name": "testtesttest"}
    _ = ApiHelper.post_a_credential(regular_client, post_body)

    # Check that we have items?
    body = ApiHelper.get_credential(regular_client)
    expect(len(body["credentials"])).not_to(equal(0))

    # do get with pagination
    body = ApiHelper.get_credential(regular_client, None, "?offset=0&limit=20")

    # add items till we need the pagination
    for _ in range(100):
        post_body = {"credential_name": "testtesttest"}
        _ = ApiHelper.post_a_credential(regular_client, post_body)

    # do get with pagination
    body = ApiHelper.get_credential(regular_client, None, "?offset=0&limit=20")
    expect(len(body["credentials"])).to(equal(20))

    # do get with pagination
    body = ApiHelper.get_credential(regular_client, None, "?offset=20&limit=20")
    expect(len(body["credentials"])).to(equal(20))
    # TODO need a test asserting the correct items return on this page
