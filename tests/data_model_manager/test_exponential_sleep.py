from data_resource_api.utils import exponential_backoff
from expects import expect, equal
import pytest


@pytest.mark.unit
def test_exponentiates_correctly():
    time_fn = exponential_backoff(1, 1.5)

    expect(time_fn()).to(equal(1.5))
    expect(time_fn()).to(equal(2.25))
    expect(time_fn()).to(equal(3.375))
    expect(time_fn()).to(equal(5.0625))
    expect(time_fn()).to(equal(7.59375))
