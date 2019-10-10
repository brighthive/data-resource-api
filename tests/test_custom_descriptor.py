from expects import expect, be_an, raise_error, have_property, equal, be_empty
from data_resource_api import ConfigurationFactory, InvalidConfigurationError
import json


class TestStartup(object):
    def test_load_descriptor(self, custom_client):
        ## Get
        route = '/tests'
        response = custom_client.get(route)
        body = json.loads(response.data)

        expect(response.status_code).to(equal(200))
        expect(body['tests']).to(be_empty)
        