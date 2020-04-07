import pytest
from data_resource_api.api.core.versioned_resource import VersionedResourceMany
from data_resource_api.app.utils.exception_handler import MethodNotAllowed
from expects import be, be_an, be_empty, equal, expect, have_property, raise_error


resource_one = "/programs/skills"
resource_two = "/providers/credentials"
api_schema = {
    "get": {},
    "custom": [
        {
            "resource": resource_one,
            "methods": [
                {
                    "get": {"enabled": False, "secured": False},
                    "put": {"enabled": False, "secured": True},
                    "patch": {"enabled": True, "secured": False},
                    "delete": {"enabled": True, "secured": True},
                }
            ],
        },
        {
            "resource": resource_two,
            "methods": [
                {
                    "get": {"enabled": False, "secured": False},
                    "put": {"enabled": False, "secured": True},
                    "patch": {"enabled": True, "secured": False},
                    "delete": {"enabled": True, "secured": True},
                }
            ],
        },
    ],
}


class TestErrorIfResourceIsDisabled:
    @pytest.mark.unit
    def test_error_if_resource_is_disabled(self):
        vr = VersionedResourceMany()

        with pytest.raises(MethodNotAllowed):
            vr.error_if_resource_is_disabled("get", resource_one, api_schema)

        with pytest.raises(MethodNotAllowed):
            vr.error_if_resource_is_disabled("put", resource_one, api_schema)

        with pytest.raises(MethodNotAllowed):
            vr.error_if_resource_is_disabled("get", resource_two, api_schema)

    @pytest.mark.unit
    def test_does_not_error_if_resource_is_enabled(self):
        vr = VersionedResourceMany()

        vr.error_if_resource_is_disabled("patch", resource_one, api_schema)
        vr.error_if_resource_is_disabled("delete", resource_one, api_schema)
        vr.error_if_resource_is_disabled("patch", resource_two, api_schema)


class TestIsSecure:
    @pytest.mark.unit
    def test_passes_when_secure(self):
        vr = VersionedResourceMany()

        expect(vr.is_secured("put", resource_one, api_schema)).to(equal(True))
        expect(vr.is_secured("delete", resource_one, api_schema)).to(equal(True))
        expect(vr.is_secured("put", resource_two, api_schema)).to(equal(True))

    @pytest.mark.unit
    def test_fails_when_not_secure(self):
        vr = VersionedResourceMany()

        expect(vr.is_secured("get", resource_one, api_schema)).to(equal(False))
        expect(vr.is_secured("patch", resource_one, api_schema)).to(equal(False))
        expect(vr.is_secured("get", resource_two, api_schema)).to(equal(False))
