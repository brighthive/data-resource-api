from data_resource_api.app.data_managers.data_resource_manager import (
    DataResourceManagerSync,
    DataResource)
from tests.schemas import (
    frameworks_descriptor,
    skills_descriptor)
from expects import expect, equal
import pytest


def setup_drm_store():
    descriptor_list = [frameworks_descriptor, skills_descriptor]
    DRM = DataResourceManagerSync(descriptors=descriptor_list)

    def create_data_resource(value: str):
        data_resource = DataResource()
        data_resource.checksum = value
        data_resource.data_resource_name = value
        data_resource.data_resource_methods = value
        data_resource.data_model_name = value
        data_resource.data_model_schema = value
        data_resource.data_model_object = value
        data_resource.model_checksum = value
        data_resource.data_resource_object = value
        return data_resource

    d1 = create_data_resource('a')
    d2 = create_data_resource('b')
    d3 = create_data_resource('c')

    DRM.data_store.append(d1)
    DRM.data_store.append(d2)
    DRM.data_store.append(d3)

    return DRM


@pytest.mark.unit
def test_data_exists():
    DRM = setup_drm_store()

    expect(
        DRM.data_resource_exists('a')
    ).to(equal(True))

    expect(
        DRM.data_resource_exists('b')
    ).to(equal(True))

    expect(
        DRM.data_resource_exists('c')
    ).to(equal(True))

    expect(
        DRM.data_resource_exists('d')
    ).to(equal(False))


@pytest.mark.unit
def test_data_changed():
    DRM = setup_drm_store()

    expect(
        DRM.data_resource_changed('a', 'a')
    ).to(equal(False))

    expect(
        DRM.data_resource_changed('a', 'b')
    ).to(equal(True))

    expect(
        DRM.data_resource_changed('d', 'a')
    ).to(equal(False))


@pytest.mark.unit
def test_get_data_index():
    DRM = setup_drm_store()

    expect(
        DRM.get_data_resource_index('a')
    ).to(equal(0))

    expect(
        DRM.get_data_resource_index('b')
    ).to(equal(1))

    expect(
        DRM.get_data_resource_index('d')
    ).to(equal(-1))
