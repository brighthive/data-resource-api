import json
from datetime import datetime

import pytest
from data_resource_api.app.utils.json_converter import safe_json_dumps


@pytest.mark.unit
def test_converter_datetime():
    dt = {"datetime": datetime(2014, 5, 12, 23, 30)}
    expected_output = {"datetime": "2014-05-12T23:30:00Z"}
    output = safe_json_dumps(dt)

    assert output == json.dumps(expected_output)
