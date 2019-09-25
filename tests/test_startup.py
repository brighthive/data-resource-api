from expects import expect, be_an, raise_error, have_property, equal, be, be_empty
from data_resource_api import ConfigurationFactory, InvalidConfigurationError
import json


class TestStartup(object):
    def test_loads(self, client):
        r1 = client.get('/credentials')
        body = json.loads(r1.data)
        print(body)

        expect(r1.status_code).to(be(200))
        expect(body['credentials']).to(be_empty)
        expect(body['links']).to(be_empty)

        r2 = client.get('/programs')
        body = json.loads(r2.data)

        expect(r2.status_code).to(be(200))
        expect(body['message']).to(equal('Access Denied'))
