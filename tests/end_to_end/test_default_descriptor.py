from expects import expect, be_an, raise_error, have_property, equal, be_empty
import json
from tests.service import ApiHelper


class TestStartup(object):
    def test_get_post_put_patch_on_one_item(self, regular_client):
        # Get
        body = ApiHelper.get_credential(regular_client)
        expect(body['credentials']).to(be_empty)
        expect(body['links']).to(be_empty)

        # Post
        post_body = {
            "credential_name": "testtesttest"
        }
        credential_id = ApiHelper.post_a_credential(regular_client, post_body)

        body = ApiHelper.get_credential(regular_client)
        expect(len(body['credentials'])).to(equal(1))

        body = ApiHelper.get_credential(regular_client, credential_id)
        expect(body['credential_name']).to(equal("testtesttest"))

        # Put
        put_body = {
            "credential_name": "asdf"
        }
        ApiHelper.put_a_credential(regular_client, put_body, credential_id)
        body = ApiHelper.get_credential(regular_client, credential_id)

        expect(body['credential_name']).to(equal("asdf"))

        # Patch
        patch_body = {
            "credential_name": "qwery"
        }
        ApiHelper.patch_a_credential(regular_client, patch_body, credential_id)
        body = ApiHelper.get_credential(regular_client, credential_id)

        expect(body['credential_name']).to(equal('qwery'))

    def test_error_on_nonexistant_field(self, regular_client):
        post_body = {
            "credential_name": "test credential",
            "doesnotexist": "doesnotexist data"
        }
        ApiHelper.post_a_credential(regular_client, post_body, 400)

    def test_programs(self, regular_client):
        _ = ApiHelper.get_program(regular_client)
        # expect(body['message']).to(equal('Access Denied'))

    def test_pagination(self, regular_client):
        post_body = {
            "credential_name": "testtesttest"
        }
        _ = ApiHelper.post_a_credential(regular_client, post_body)

        # Check that we have items?
        body = ApiHelper.get_credential(regular_client)
        expect(len(body['credentials'])).not_to(equal(0))

        # do get with pagination
        body = ApiHelper.get_credential(regular_client, None, "?offset=0&limit=20")

        # add items till we need the pagination
        for _ in range(100):
            post_body = {"credential_name": "testtesttest"}
            _ = ApiHelper.post_a_credential(regular_client, post_body)

        # do get with pagination
        body = ApiHelper.get_credential(regular_client, None, "?offset=0&limit=20")
        expect(len(body['credentials'])).to(equal(20))

        # do get with pagination
        body = ApiHelper.get_credential(regular_client, None, "?offset=20&limit=20")
        expect(len(body['credentials'])).to(equal(20))
        # TODO need a test asserting the correct items return on this page
