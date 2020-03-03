from data_resource_api.app.utils.descriptor import DescriptorFileHelper
from tests.schemas import (
    frameworks_descriptor)
from expects import expect, equal


class TestDescriptorFileHelper():
    def test_check_if_path_exists(self):
        # expect it to raise an error when given a directory that doesnt exist

        # expect it not to raise an error when given a real directory
        pass

    def test_get_only_json_files(self):
        test_dir = './tests/io_test_files'
        fake_self = object
        # TODO how do i test a function directly while passing a fake self>
        # helper = DescriptorFileHelper.__class__(fake_self, test_dir)

        # expect(fake_self.schemas).to(equal(['invalid_json.json', 'valid_json.json']))

    def test_returns_correctly(self):
        pass
