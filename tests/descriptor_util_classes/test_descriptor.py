from data_resource_api.app.utils.descriptor import Descriptor
from tests.schemas import (
    frameworks_descriptor)
from expects import expect, equal
import pytest


@pytest.mark.unit
def test_load():
    # does not raise an error
    _ = Descriptor(frameworks_descriptor)


@pytest.mark.unit
@pytest.mark.skip
def test_fail_on_bad_json():
    # desc = Descriptor()
    pass


@pytest.mark.unit
def test_get_table_name():
    desc = Descriptor(frameworks_descriptor)
    table_name = desc.table_name
    expect(table_name).to(
        equal(frameworks_descriptor['datastore']['tablename']))


@pytest.mark.unit
def test_get_table_schema():
    desc = Descriptor(frameworks_descriptor)
    table_schema = desc.table_schema
    expect(table_schema).to(
        equal(frameworks_descriptor['datastore']['schema']))


@pytest.mark.unit
def test_get_api_schema():
    desc = Descriptor(frameworks_descriptor)
    api_schema = desc.api_schema
    expect(api_schema).to(
        equal(frameworks_descriptor['api']['methods'][0]))


@pytest.mark.unit
def test_descriptor_with_no_file_name():
    desc = Descriptor(frameworks_descriptor)
    file_name = desc.file_name
    expect(file_name).to(equal("frameworks.json"))


@pytest.mark.unit
def test_descriptor_with_file_name():
    desc = Descriptor(frameworks_descriptor, "asdf.json")
    file_name = desc.file_name
    expect(file_name).to(equal("asdf.json"))
