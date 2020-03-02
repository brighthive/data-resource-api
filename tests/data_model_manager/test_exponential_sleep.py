from data_resource_api.utils import exponential_backoff
from expects import expect, be_an, raise_error, have_property, equal


class TestExponentialBackoff():
    def test_exponentiates_correctly(self):
        time_fn = exponential_backoff(1, 1.5)

        expect(time_fn()).to(equal(1.5))
        expect(time_fn()).to(equal(2.25))
        expect(time_fn()).to(equal(3.375))
        expect(time_fn()).to(equal(5.0625))
        expect(time_fn()).to(equal(7.59375))
