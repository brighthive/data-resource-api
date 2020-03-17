from expects import expect, be_an, raise_error, have_property, equal, be_empty
import json


class TestStartup(object):
    def test_credentials(self, regular_client):
        # Load json descriptor

        # Get
        route = '/credentials'
        response = regular_client.get(route)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        expect(body['credentials']).to(be_empty)
        expect(body['links']).to(be_empty)

        # Login ?

        # Post
        post_body = {
            "credential_name": "testtesttest"
        }
        response = regular_client.post(route, json=post_body)

        expect(response.status_code).to(equal(201))

        body = json.loads(response.data)
        credential_id = body['id']

        # Check all credentials
        response = regular_client.get(route)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        expect(len(body['credentials'])).to(equal(1))

        # Check for one item
        response = regular_client.get(f'{route}/{credential_id}')
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        expect(body['credential_name']).to(equal("testtesttest"))

        # Put
        put_body = {
            "credential_name": "asdf"
        }
        response = regular_client.put(
            f'{route}/{credential_id}', json=put_body)
        expect(response.status_code).to(equal(201))

        response = regular_client.get(f'{route}/{credential_id}')
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        expect(body['credential_name']).to(equal("asdf"))

        # expect(body['credential_name']).to(equal('asdf'))

        # Patch
        patch_body = {
            "credential_name": "qwery"
        }
        response = regular_client.patch(
            f'{route}/{credential_id}', json=patch_body)
        body = json.loads(response.data)
        expect(response.status_code).to(equal(201))

        response = regular_client.get(f'{route}/{credential_id}')
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        expect(body['credential_name']).to(equal('qwery'))

    def test_error_on_nonexistant_field(self, regular_client):
        route = '/credentials'
        post_body = {
            "credential_name": "test credential",
            "doesnotexist": "doesnotexist data"
        }
        response = regular_client.post(route, json=post_body)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(400))

    def test_programs(self, regular_client):
        response = regular_client.get('/programs')
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        # expect(body['message']).to(equal('Access Denied'))

    def test_pagination(self, regular_client):
        def post_a_credential():
            post_body = {
                "credential_name": "testtesttest"
            }
            response = regular_client.post('/credentials', json=post_body)

            expect(response.status_code).to(equal(201))

            body = json.loads(response.data)
            return body

        body = post_a_credential()
        print(json.dumps(body, indent=4))

        # do regular get
        route = '/credentials'
        response = regular_client.get(route)
        body = json.loads(response.data)
        print(json.dumps(body, indent=4))

        expect(response.status_code).to(equal(200))
        expect(len(body['credentials'])).not_to(equal(0))

        # do get with pagination
        route = '/credentials?offset=0&limit=20'
        response = regular_client.get(route)
        body = json.loads(response.data)
        print(json.dumps(body, indent=4))

        expect(response.status_code).to(equal(200))

        # add items till we need the pagination
        for _ in range(100):
            body = post_a_credential()
            print(json.dumps(body, indent=4))

        # do get with pagination
        route = '/credentials?offset=0&limit=20'
        response = regular_client.get(route)
        body = json.loads(response.data)
        print(json.dumps(body, indent=4))
        expect(len(body['credentials'])).to(equal(20))

        # do get with pagination
        route = '/credentials?offset=20&limit=20'
        response = regular_client.get(route)
        body = json.loads(response.data)
        print(json.dumps(body, indent=4))
        # expect(len(body['credentials'])).to(equal(20))
