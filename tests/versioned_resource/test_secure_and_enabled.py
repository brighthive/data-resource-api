from data_resource_api.api.core.versioned_resource import VersionedResourceMany
from expects import expect, be_an, raise_error, have_property, equal, be_empty, be
from data_resource_api.app.exception_handler import MethodNotAllowed
import pytest


resource_one = '/programs/skills'
resource_two = '/providers/credentials'

api_schema = {
    'get': {},
    'custom': [
        {
            'resource': resource_one,
            'methods': [
                {
                    'get': {
                        "enabled": False,
                        "secured": False
                    },
                    'put': {
                        'enabled': False,
                        'secured': True
                    },
                    'patch': {
                        'enabled': True,
                        'secured': False
                    },
                    'delete': {
                        'enabled': True,
                        'secured': True
                    }
                }
            ]
        }, {
            'resource': resource_two,
            'methods': [
                {
                    'get': {
                        "enabled": False,
                        "secured": False
                    },
                    'put': {
                        'enabled': False,
                        'secured': True
                    },
                    'patch': {
                        'enabled': True,
                        'secured': False
                    },
                    'delete': {
                        'enabled': True,
                        'secured': True
                    }
                }
            ]
        }
    ]
}


class TestErrorIfResourceIsDisabled(object):
    def test_error_if_resource_is_disabled(self):
        vr = VersionedResourceMany()

        with pytest.raises(MethodNotAllowed):
            vr.error_if_resource_is_disabled('get', resource_one, api_schema)

        with pytest.raises(MethodNotAllowed):
            vr.error_if_resource_is_disabled('put', resource_one, api_schema)

        with pytest.raises(MethodNotAllowed):
            vr.error_if_resource_is_disabled('get', resource_two, api_schema)

    def test_does_not_error_if_resource_is_enabled(self):
        vr = VersionedResourceMany()

        vr.error_if_resource_is_disabled('patch', resource_one, api_schema)
        vr.error_if_resource_is_disabled('delete', resource_one, api_schema)
        vr.error_if_resource_is_disabled('patch', resource_two, api_schema)


class TestIsSecure(object):
    def test_passes_when_secure(self):
        vr = VersionedResourceMany()

        expect(vr.is_secured('put', resource_one, api_schema)).to(equal(True))
        expect(vr.is_secured('delete', resource_one, api_schema)).to(equal(True))
        expect(vr.is_secured('put', resource_two, api_schema)).to(equal(True))

    def test_fails_when_not_secure(self):
        vr = VersionedResourceMany()

        expect(vr.is_secured('get', resource_one, api_schema)).to(equal(False))
        expect(vr.is_secured('patch', resource_one, api_schema)).to(equal(False))
        expect(vr.is_secured('get', resource_two, api_schema)).to(equal(False))
