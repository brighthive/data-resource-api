import json
import os
import shutil

import pytest
from data_resource_api.app.utils.descriptor import (
    DescriptorFromFile,
    DescriptorsFromDirectory,
)

IO_TEST_FILES = os.path.join(os.path.dirname(__file__), "..", "io_test_files")
INVALID_JSON = os.path.join(IO_TEST_FILES, "invalid_json.json")


def test_raises_on_invalid_json():
    """DescriptorFromFile must raise RuntimeError for invalid JSON, not crash with NameError."""
    schema_dir = os.path.dirname(INVALID_JSON)
    file_name = os.path.basename(INVALID_JSON)
    with pytest.raises(RuntimeError, match="JSON is probably invalid"):
        DescriptorFromFile(schema_dir, file_name)


def test_raises_on_directory_instead_of_file(tmp_path):
    """DescriptorFromFile must raise RuntimeError when given a directory path."""
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    with pytest.raises(RuntimeError, match="Cannot open a directory"):
        DescriptorFromFile(str(tmp_path), "subdir")


def test_skips_invalid_json_and_continues(tmp_path):
    """DescriptorsFromDirectory must skip invalid JSON files and keep loading valid ones."""
    shutil.copy(INVALID_JSON, tmp_path / "invalid_json.json")

    valid_descriptor = {
        "api": {
            "resource": "frameworks",
            "methods": [{"get": {"enabled": True, "secured": False, "grants": []}}],
        },
        "datastore": {
            "tablename": "frameworks",
            "restricted_fields": [],
            "schema": {
                "fields": [
                    {"name": "id", "type": "integer", "title": "id", "required": False}
                ],
                "primaryKey": "id",
            },
        },
    }
    with open(tmp_path / "valid_descriptor.json", "w") as f:
        json.dump(valid_descriptor, f)

    descriptors = list(DescriptorsFromDirectory([str(tmp_path)]).iter_files())
    assert len(descriptors) == 1
    assert descriptors[0].table_name == "frameworks"
