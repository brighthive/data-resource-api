import pytest
import json
from tests.service import ApiHelper
from expects import expect, be_an, raise_error, have_property, equal, be_empty


ROUTE = '/alltypes'


def run_query(client, key, value, expected_value=None):
    if not expected_value:
        expected_value = value
    post_body = {
        key: value
    }
    id_ = ApiHelper.everything_post(ROUTE, client, post_body)
    resp_data = ApiHelper.everything_get(ROUTE, client, id_)
    resp = json.loads(resp_data)

    # response = json.dumps(resp, sort_keys=True)
    # expected_output = json.dumps(expected_string, sort_keys=True)
    expect(resp[key]).to(equal(expected_value))
    assert type(resp[key]) == type(expected_value)


def test_string(everything_client):
    # {
    #     "name": "string",
    #     "title": "string",
    #     "type": "string",
    #     "required": False
    # },
    run_query(everything_client, "string", "asdf1234")


# @pytest.mark.xfail
def test_number(everything_client):
    # {
    #     "name": "number",
    #     "title": "number",
    #     "type": "number",
    #     "required": False
    # },
    run_query(everything_client, "number", 1234.0)
    run_query(everything_client, "number", 1234, 1234.0)


# @pytest.mark.xfail
def test_integer(everything_client):
    # {
    #     "name": "integer",
    #     "title": "integer",
    #     "type": "integer",
    #     "required": False
    # },
    run_query(everything_client, "integer", 1234)


# @pytest.mark.xfail
def test_boolean(everything_client):
    # {
    #     "name": "boolean",
    #     "title": "boolean",
    #     "type": "boolean",
    #     "required": False
    # },
    run_query(everything_client, "boolean", False)
    run_query(everything_client, "boolean", True)


# @pytest.mark.xfail
def test_object(everything_client):
    # {
    #     "name": "object",
    #     "title": "object",
    #     "type": "object",
    #     "required": False
    # },
    run_query(everything_client, "object", {"json": "test"})


@pytest.mark.skip
def test_array(everything_client):
    # {
    #     "name": "array",
    #     "title": "array",
    #     "type": "array",
    #     "required": False
    # },
    run_query(everything_client, "array", ['one', 'two', 'three'])


@pytest.mark.xfail
def test_date(everything_client):
    # {
    #     "name": "date",
    #     "title": "date",
    #     "type": "date",
    #     "required": False
    # },
    run_query(everything_client, "date", "2012-04-23")


@pytest.mark.xfail
def test_time(everything_client):
    # {
    #     "name": "time",
    #     "title": "time",
    #     "type": "time",
    #     "required": False
    # },
    run_query(everything_client, "time", "18:25:43.511Z")


@pytest.mark.xfail
def test_datetime(everything_client):
    # {
    #     "name": "datetime",
    #     "title": "datetime",
    #     "type": "datetime",
    #     "required": False
    # },
    run_query(everything_client, "datetime", "2012-04-23T18:25:43.511Z")


# @pytest.mark.xfail
def test_year(everything_client):
    # {
    #     "name": "year",
    #     "title": "year",
    #     "type": "year",
    #     "required": False
    # },
    run_query(everything_client, "year", 2012)


@pytest.mark.xfail
def test_yearmonth(everything_client):
    # {
    #     "name": "yearmonth",
    #     "title": "yearmonth",
    #     "type": "yearmonth",
    #     "required": False
    # },
    run_query(everything_client, "yearmonth", "2012-11")


# @pytest.mark.xfail
def test_duration(everything_client):
    # {
    #     "name": "duration",
    #     "title": "duration",
    #     "type": "duration",
    #     "required": False
    # },
    run_query(everything_client, "duration", 11)


# @pytest.mark.xfail
def test_geopoint(everything_client):
    # {
    #     "name": "geopoint",
    #     "title": "geopoint",
    #     "type": "geopoint",
    #     "required": False
    # },
    run_query(everything_client, "geopoint", "41.12,-71.34")


# @pytest.mark.xfail
def test_geojson(everything_client):
    # {
    #     "name": "geojson",
    #     "title": "geojson",
    #     "type": "geojson",
    #     "required": False
    # },
    run_query(everything_client, "geopoint", "41.12,-71.34")
    # https://geojson.org/ # TODO we don't support this


# @pytest.mark.xfail
def test_any(everything_client):
    # {
    #     "name": "any",
    #     "title": "any",
    #     "type": "any",
    #     "required": False
    # }
    run_query(everything_client, "any", "asdf1234")
