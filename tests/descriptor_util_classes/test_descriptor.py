from data_resource_api.app.descriptor import Descriptor
from tests.schemas import (
    frameworks_descriptor)
from expects import expect, equal


class TestDescriptorClass():
    def test_load(self):
        # does not raise an error
        desc = Descriptor(frameworks_descriptor)

    def test_fail_on_bad_json(self):
        # desc = Descriptor()
        pass

    def test_get_table_name(self):
        desc = Descriptor(frameworks_descriptor)
        table_name = desc.table_name
        expect(table_name).to(equal(frameworks_descriptor['datastore']['tablename']))

    def test_get_table_schema(self):
        desc = Descriptor(frameworks_descriptor)
        table_schema = desc.table_schema
        expect(table_schema).to(equal(frameworks_descriptor['datastore']['schema']))

    def test_get_api_schema(self):
        desc = Descriptor(frameworks_descriptor)
        api_schema = desc.api_schema
        expect(api_schema).to(equal(frameworks_descriptor['api']['methods'][0]))

    def test_descriptor_with_no_file_name(self):
        desc = Descriptor(frameworks_descriptor)
        file_name = desc.file_name
        expect(file_name).to(equal("frameworks.json"))

    def test_descriptor_with_file_name(self):
        desc = Descriptor(frameworks_descriptor, "asdf.json")
        file_name = desc.file_name
        expect(file_name).to(equal("asdf.json"))
