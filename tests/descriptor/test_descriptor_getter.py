from data_resource_api.app.descriptor import DescriptorsGetter
from tests.schemas import (
    frameworks_descriptor)
from expects import expect, equal
import pytest

test_descriptor_dir = './tests/io_test_files/'


class TestDescriptorGetterWithNothing():
    def test_load_with_nothing(self):
        desc = DescriptorsGetter()

    def test_yields_descriptors_from_dir(self):
        desc = DescriptorsGetter()
        descriptors = desc.iter_descriptors()

        with pytest.raises(StopIteration):
            next(descriptors)

class TestDescriptorGetterWithDir():
    def test_load_with_dir(self):
        desc = DescriptorsGetter([test_descriptor_dir])

    def test_yields_descriptors_from_dir(self):
        desc = DescriptorsGetter([test_descriptor_dir])
        descriptors = desc.iter_descriptors()

        # Expect an error is not raised (valid_json)
        next(descriptors)

        # Expect an error is raised (invalid_json)
        with pytest.raises(RuntimeError):
            expect(next(descriptors)).to(equal(2))

        with pytest.raises(StopIteration):
            next(descriptors)

class TestDescriptorGetterWithCustom():
    def test_load_with_custom(self):
        desc = DescriptorsGetter([], [frameworks_descriptor])

    def test_yields_descriptors_from_custom(self):
        desc = DescriptorsGetter([], [frameworks_descriptor])
        descriptors = desc.iter_descriptors()

        # Expect an error is not raiased (valid_json)
        next(descriptors)

# class TestDescriptorGetterWithDirAndCustom():
    # def test_load_with_dir_and_custom(self):
    #     desc = DescriptorsGetter([test_descriptor_dir], [frameworks_descriptor])

    # def test_yields_descriptors_from_dir_and_custom(self):
    #     pass