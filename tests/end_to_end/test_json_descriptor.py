import json

from tests.service import ApiHelper

import pytest
from expects import be_an, be_empty, equal, expect, have_property, raise_error


@pytest.mark.requiresdb
def test_json_posts_and_returns_correctly(json_client):
    c = json_client

    json_body = {"test": 1234, "obj": {"key": "value"}}

    json_id = ApiHelper.post_a_json(c, json_body)

    resp = ApiHelper.get_a_json_by_id(c, json_id)

    expect(json.dumps(resp["json"], sort_keys=True)).to(
        equal(json.dumps(json_body, sort_keys=True))
    )


@pytest.mark.requiresdb
def test_nested_str_in_json_posts_and_returns_correctly(json_client):
    c = json_client

    json_body = {"test": 1234, "obj": r'{"key": "value"\}'}

    json_id = ApiHelper.post_a_json(c, json_body)

    resp = ApiHelper.get_a_json_by_id(c, json_id)

    expect(json.dumps(resp["json"], sort_keys=True)).to(
        equal(json.dumps(json_body, sort_keys=True))
    )


@pytest.mark.requiresdb
def test_nested_nested_str_in_json_posts_and_returns_correctly(json_client):
    c = json_client

    json_body = {"test": 1234, "obj": {"but what about this": r'{"key": "value"\}'}}

    json_id = ApiHelper.post_a_json(c, json_body)

    resp = ApiHelper.get_a_json_by_id(c, json_id)

    expect(json.dumps(resp["json"], sort_keys=True)).to(
        equal(json.dumps(json_body, sort_keys=True))
    )


@pytest.mark.requiresdb
def test_long_str(json_client):
    c = json_client

    json_body = {
        "data": '{"uuid": "e997a2f7-2809-4543-b55e-edff65d66c62", "first_name": "Aniya", "last_name": "Sauer", "gender": "Female/Woman", "email": "lambda-test-Tate_Emard64@yahoo.com", "phone": null, "phone_type": null, "resume": null, "street": null, "street2": null, "city": null, "state": null, "zipcode": null, "country": "US", "birthdate": "1990-12-12", "highest_education": null, "work_authorized": true, "preferred_language": "english", "unemployment_insurance": null, "race": null, "selective_service": null, "veteran": "{\\"non_veteran\\": true}", "created_at": "2019-10-01 08:45:35 -0600", "last_login": "", "journey_role": null, "ssn_last4": null, "high_school_graduation_year": null, "associated_organization": null, "legacy_data_consent": null, "work_histories": [], "most_recent_completed_assessment": null, "user_employment": {"currently_employed": null, "laid_off": null, "mass_layoff": null, "fired": null, "changing_careers": null, "current_industry": null, "seasonal": true}, "military_histories": [], "certifications": [], "education_histories": [], "language_proficiency": [], "user_question_data": {"job_difficulties": null, "assistance": null, "looking_for": "{\\"job\\": true}", "va_benefits": null, "homeless_risk": null, "incarcerated": null, "divorced": null, "looking_change_self_employment": null, "low_income": null, "housing_situation": null, "satisfied_income": null, "aspired_education": null, "education_training_info": null}'
    }

    json_id = ApiHelper.post_a_json(c, json_body)

    resp = ApiHelper.get_a_json_by_id(c, json_id)

    expect(json.dumps(resp["json"], sort_keys=True)).to(
        equal(json.dumps(json_body, sort_keys=True))
    )
