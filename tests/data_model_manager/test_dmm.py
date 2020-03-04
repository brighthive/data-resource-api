from data_resource_api.app.data_managers.data_model_manager import (
    DataModelManagerSync,
    DataModelDescriptor)
from expects import expect, be_an, raise_error, have_property, equal
from tests.schemas import (
    frameworks_descriptor,
    skills_descriptor,
    credentials_descriptor,
    programs_descriptor)
import pytest


def setup_dmm_store():
    descriptor_list = [frameworks_descriptor, skills_descriptor]
    DMM = DataModelManagerSync(descriptors=descriptor_list)

    d1 = DataModelDescriptor('a', 'a', 'a')
    d2 = DataModelDescriptor('b', 'b', 'b')
    d3 = DataModelDescriptor('c', 'c', 'c')

    DMM.data_store.append(d1)
    DMM.data_store.append(d2)
    DMM.data_store.append(d3)

    return DMM


class TestDataModelManager():
    @pytest.mark.xfail  # this is failing because of a strange interaction with juncholder
    # this test will pass if run by itself -- if run with all other tests it
    # fails.
    def test_load_descriptor_into_sql_alchemy_model(self, base):
        table_list = list(base.metadata.tables.keys())
        expect(table_list).to(equal([]))

        DMM = DataModelManagerSync(base=base)
        DMM.load_descriptor_into_sql_alchemy_model(frameworks_descriptor)
        table_list = list(base.metadata.tables.keys())

        expect(table_list).to(equal(['frameworks/skills', 'frameworks']))

    @pytest.mark.skip
    def start_with_dir(self, base):
        descriptor_directory = './tests/io_test_files'
        DMM = DataModelManagerSync(base=base)

    @pytest.mark.skip
    def start_with_list_of_descriptors(self, base):
        descriptor_list = [frameworks_descriptor, skills_descriptor]
        DMM = DataModelManagerSync(base=base, descriptors=descriptor_list)

    def test_data_exists(self):
        DMM = setup_dmm_store()
        expect(
            DMM.data_model_exists('a')
        ).to(equal(True))

        expect(
            DMM.data_model_exists('b')
        ).to(equal(True))

        expect(
            DMM.data_model_exists('c')
        ).to(equal(True))

        expect(
            DMM.data_model_exists('d')
        ).to(equal(False))
