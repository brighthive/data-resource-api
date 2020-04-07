from tests.schemas import frameworks_descriptor

import pytest
from data_resource_api.app.utils.descriptor import DescriptorsFromDirectory
from expects import equal, expect


@pytest.mark.skip
def test_check_if_path_exists(self):
    # expect it to raise an error when given a directory that doesnt exist

    # expect it not to raise an error when given a real directory
    pass


@pytest.mark.skip
def test_get_only_json_files(self):
    test_dir = "./tests/io_test_files"
    fake_self = object
    # TODO how do i test a function directly while passing a fake self>
    # helper = DescriptorsFromDirectory.__class__(fake_self, test_dir)

    # expect(fake_self.schemas).to(equal(['invalid_json.json', 'valid_json.json']))


@pytest.mark.skip
def test_returns_correctly(self):
    pass
