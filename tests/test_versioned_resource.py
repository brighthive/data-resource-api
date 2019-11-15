from data_resource_api.api.core.versioned_resource import VersionedResourceMany
from expects import expect, be_an, raise_error, have_property, equal, be_empty, be
from data_resource_api.app.exception_handler import MethodNotAllowed
import pytest


class TestErrorIfResourceIsDisabled(object):
    def test_error_if_resource_is_disabled(self):
        vr = VersionedResourceMany()
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
                            }
                        }
                    ]
                }
            ]
        }

        with pytest.raises(MethodNotAllowed):
            vr.error_if_resource_is_disabled('get', resource_one, api_schema)

        with pytest.raises(MethodNotAllowed):
            vr.error_if_resource_is_disabled('put', resource_one, api_schema)

        with pytest.raises(MethodNotAllowed):
            vr.error_if_resource_is_disabled('get', resource_two, api_schema)

    def test_does_not_error_if_resource_is_enabled(self):
        vr = VersionedResourceMany()
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
                                "enabled": True,
                                "secured": False
                            },
                            'put': {
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
                                "enabled": True,
                                "secured": False
                            }
                        }
                    ]
                }
            ]
        }

        vr.error_if_resource_is_disabled('get', resource_one, api_schema)
        vr.error_if_resource_is_disabled('put', resource_one, api_schema)
        vr.error_if_resource_is_disabled('get', resource_two, api_schema)
