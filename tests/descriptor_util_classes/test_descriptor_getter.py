from data_resource_api.app.utils.descriptor import DescriptorsLoader
from tests.schemas import (
    frameworks_descriptor)
from expects import expect, equal
import pytest

test_descriptor_dir = './tests/io_test_files/'


class TestDescriptorGetterWithNothing():
    @pytest.mark.unit
    def test_load_with_nothing(self):
        _ = DescriptorsLoader()

    @pytest.mark.unit
    def test_yields_descriptors_from_dir(self):
        desc = DescriptorsLoader()
        descriptors = desc.iter_descriptors()

        with pytest.raises(StopIteration):
            next(descriptors)


class TestDescriptorGetterWithDir():
    @pytest.mark.unit
    def test_load_with_dir(self):
        _ = DescriptorsLoader([test_descriptor_dir])

    @pytest.mark.unit
    def test_yields_descriptors_from_dir(self):
        desc = DescriptorsLoader([test_descriptor_dir])
        descriptors = desc.iter_descriptors()

        # Expect an error is not raised (valid_json)
        next(descriptors)

        # Expect the next item is skipped (invalid_json)
        with pytest.raises(StopIteration):
            next(descriptors)


class TestDescriptorGetterWithCustom():
    @pytest.mark.unit
    def test_load_with_custom(self):
        _ = DescriptorsLoader([], [frameworks_descriptor])

    @pytest.mark.unit
    def test_yields_descriptors_from_custom(self):
        desc = DescriptorsLoader([], [frameworks_descriptor])
        descriptors = desc.iter_descriptors()

        next(descriptors)


class TestDescriptorGetterWithDirAndCustom():
    @pytest.mark.unit
    def test_load_with_dir_and_custom(self):
        _ = DescriptorsLoader(
            [test_descriptor_dir],
            [frameworks_descriptor])

    @pytest.mark.unit
    def test_yields_descriptors_from_dir_and_custom(self):
        desc = DescriptorsLoader(
            [test_descriptor_dir],
            [frameworks_descriptor])
        descriptors = desc.iter_descriptors()

        next(descriptors)

        next(descriptors)

        with pytest.raises(StopIteration):
            next(descriptors)
