from data_resource_api.api.v1_0_0.utils import safe_json_dumps
from datetime import datetime
import json


def test_converter_datetime():
    dt = {
        "datetime": datetime(2014, 5, 12, 23, 30)
    }
    expected_output = {
        "datetime": "2014-05-12T23:30:00Z"
    }
    output = safe_json_dumps(dt)

    assert output == json.dumps(expected_output)
