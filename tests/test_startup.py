from expects import expect, be_an, raise_error, have_property, equal, be_empty
from data_resource_api import ConfigurationFactory, InvalidConfigurationError
import json


class TestStartup(object):
    def test_credentials(self, client):
        ## Get
        route = '/credentials'
        response = client.get(route)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        expect(body['credentials']).to(be_empty)
        expect(body['links']).to(be_empty)
        
        ## Login ?

        ## Post
        post_body = {
            "credential_name": "testtesttest"
        }
        response = client.post(route, json=post_body)
        expect(response.status_code).to(equal(201))

        ## Check for one item
        response = client.get(route)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        expect(len(body['credentials'])).to(equal(1))
        

    def test_programs(self, client):
        response = client.get('/programs')
        body = json.loads(response.data)

        expect(response.status_code).to(equal(401))
        expect(body['message']).to(equal('Access Denied'))
