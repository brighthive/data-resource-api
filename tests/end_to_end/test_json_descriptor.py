from expects import expect, be_an, raise_error, have_property, equal, be_empty
from data_resource_api import ConfigurationFactory, InvalidConfigurationError
import json
import pytest

class TestJson():
    @pytest.mark.xfail
    def test_json_posts_and_returns_correctly(self, json_client):
        pass