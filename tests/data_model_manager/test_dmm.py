from data_resource_api.app.data_managers.data_model_manager import (
    DataModelManagerSync,
    DataModelDescriptor)
from expects import expect, equal
from tests.schemas import (
    frameworks_descriptor,
    skills_descriptor)
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

# @pytest.mark.skip
# def test_add_checksum(no_db_dmm, mocker):
#     mocker.patch('data_resource_api.app.utils.db_handler.DBHandler.revision', return_value=True)
#     mocker.patch('data_resource_api.app.utils.db_handler.DBHandler.upgrade', return_value=True)
#     fn_update_model_checksum = mocker.patch('data_resource_api.app.utils.db_handler.DBHandler.add_model_checksum', return_value=True)
#     desc = Descriptor(frameworks_descriptor)

#     no_db_dmm.update_data_model(desc)

#     fn_update_model_checksum.assert_called()


@pytest.mark.unit
@pytest.mark.xfail  # this is failing because of a strange interaction with juncholder
# this test will pass if run by itself -- if run with all other tests it
# fails.
def test_load_descriptor_into_sql_alchemy_model(base):
    table_list = list(base.metadata.tables.keys())
    expect(table_list).to(equal([]))

    DMM = DataModelManagerSync(base=base)
    DMM.load_descriptor_into_sql_alchemy_model(frameworks_descriptor)
    table_list = list(base.metadata.tables.keys())

    expect(table_list).to(equal(['frameworks/skills', 'frameworks']))


@pytest.mark.unit
@pytest.mark.skip
def start_with_dir(base):
    descriptor_directory = './tests/io_test_files'
    DMM = DataModelManagerSync(base=base)


@pytest.mark.unit
@pytest.mark.skip
def start_with_list_of_descriptors(base):
    descriptor_list = [frameworks_descriptor, skills_descriptor]
    DMM = DataModelManagerSync(base=base, descriptors=descriptor_list)


@pytest.mark.unit
def test_data_exists():
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


@pytest.mark.unit
def test_data_changed():
    DMM = setup_dmm_store()

    expect(
        DMM.data_model_changed('a', 'a')
    ).to(equal(False))

    expect(
        DMM.data_model_changed('a', 'b')
    ).to(equal(True))

    expect(
        DMM.data_model_changed('d', 'a')
    ).to(equal(False))


@pytest.mark.unit
def test_get_data_index():
    DMM = setup_dmm_store()

    expect(
        DMM.get_data_model_index('a')
    ).to(equal(0))

    expect(
        DMM.get_data_model_index('b')
    ).to(equal(1))

    expect(
        DMM.get_data_model_index('d')
    ).to(equal(-1))
