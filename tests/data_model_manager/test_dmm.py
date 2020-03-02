from data_resource_api.app.data_model_manager import DataModelManagerSync
from expects import expect, be_an, raise_error, have_property, equal
from tests.schemas import (
    frameworks_descriptor,
    skills_descriptor,
    credentials_descriptor,
    programs_descriptor)
import pytest


class TestDataModelManager():
    @pytest.mark.xfail  # this is failing because of a strange interaction with juncholder
    # this test will pass if run by itself -- if run with all other tests it fails.
    def test_load_descriptor_into_sql_alchemy_model(self, base):
        table_list = list(base.metadata.tables.keys())
        expect(table_list).to(equal([]))

        DMM = DataModelManagerSync(base)
        DMM.load_descriptor_into_sql_alchemy_model(frameworks_descriptor)
        table_list = list(base.metadata.tables.keys())

        expect(table_list).to(equal(['frameworks/skills', 'frameworks']))

    def start_with_dir(self, base):
        descriptor_directory = './tests/io_test_files'
        DMM = DataModelManagerSync(Base)

    def start_with_list_of_descriptors(self, base):
        descriptor_list = [frameworks_descriptor, skills_descriptor]
        DMM = DataModelManagerSync(Base, descriptor_list)